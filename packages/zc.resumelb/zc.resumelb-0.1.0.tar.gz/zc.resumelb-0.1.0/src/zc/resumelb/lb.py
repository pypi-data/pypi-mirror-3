from bisect import bisect_left, insort
import gevent
import gevent.hub
import gevent.pywsgi
import gevent.socket
import llist
import logging
import re
import sys
import webob
import zc.parse_addr
import zc.resumelb.util

block_size = 1<<16

logger = logging.getLogger(__name__)

retry_methods = set(('GET', 'HEAD'))

default_disconnect_message = '''
<html><meta http-equiv="refresh" content="1"><body>
The server was unable to handle your request due to a transient failure.
Please try again.
</body></html>
'''

class LB:

    def __init__(self, worker_addrs, classifier,
                 disconnect_message=default_disconnect_message,
                 **pool_settings):
        self.classifier = classifier
        self.disconnect_message = disconnect_message
        self.pool = Pool(**pool_settings)
        self.update_settings = self.pool.update_settings
        self.workletts = {}
        self.set_worker_addrs(worker_addrs)

    def set_worker_addrs(self, addrs):
        addrs = set(addrs)
        workletts = self.workletts
        old = list(workletts)
        for addr in addrs:
            if addr not in workletts:
                workletts[addr] = gevent.spawn(self.connect, addr, workletts)

        for addr in old:
            if addr not in addrs:
                workletts.pop(addr)

    connect_sleep = 1.0
    def connect(self, addr, workletts):
        while addr in workletts:
            try:
                socket = gevent.socket.create_connection(addr)
                Worker(self.pool, socket, addr)
            except Exception:
                logger.exception('lb connecting to %r', addr)
                gevent.sleep(self.connect_sleep)

    def stop(self):
        for g in self.workletts.values():
            g.kill()
        self.workletts.clear()

    def handle_wsgi(self, env, start_response):
        rclass = self.classifier(env)
        logger.debug('wsgi: %s', rclass)

        while 1:
            worker = self.pool.get(rclass)
            try:
                result = worker.handle(rclass, env, start_response)
                self.pool.put(worker)
                return result
            except zc.resumelb.util.Disconnected:
                if (int(env.get('CONTENT_LENGTH', 0)) == 0 and
                    env.get('REQUEST_METHOD') in retry_methods
                    ):
                    logger.info("retrying %s", env)
                else:
                    return webob.Response(
                        status = '502 Bad Gateway',
                        content_type= 'text/html',
                        body = self.disconnect_message
                        )(env, start_response)

class Pool:

    def __init__(self, unskilled_score=1.0, variance=4.0, backlog_history=9):
        self.unskilled_score = unskilled_score
        self.variance = variance
        self.backlog_history = backlog_history
        self._update_worker_decay()

        self.workers = set()
        self.nworkers = 0
        self.unskilled = llist.dllist()
        self.skilled = {}   # rclass -> {[(score, workers)]}
        self.event = gevent.event.Event()
        _init_backlog(self)

    def update_settings(self, settings):
        for name in ('unskilled_score', 'variance', 'backlog_history'):
            if name in settings:
                setattr(self, name, settings[name])

        if 'backlog_history' in settings:
            self._update_worker_decay()
            self._update_decay()

    def _update_decay(self):
        if self.nworkers:
            self.decay = 1.0 - 1.0/(self.backlog_history*2*self.nworkers)

    def _update_worker_decay(self):
        self.worker_decay = 1.0 - 1.0/(self.backlog_history*2)

    def __repr__(self):
        outl = []
        out = outl.append
        out('Request classes:')
        for (rclass, skilled) in sorted(self.skilled.items()):
            out('  %s: %s'
                % (rclass,
                   ', '.join(
                       '%s(%s,%s)' %
                       (worker, score, worker.mbacklog)
                       for (score, worker) in sorted(skilled)
                   ))
                )
        out('Backlogs:')
        out("  overall backlog: %s Decayed: %s Avg: %s" % (
            self.backlog, self.mbacklog,
            (self.mbacklog / self.nworkers) if self.nworkers else None
            ))
        backlogs = {}
        for worker in self.workers:
            backlogs.setdefault(worker.backlog, []).append(worker)
        for backlog, workers in sorted(backlogs.items()):
            out('  %s: %r' % (backlog, sorted(workers)))
        return '\n'.join(outl)

    def new_resume(self, worker, resume):
        skilled = self.skilled
        workers = self.workers

        if worker in workers:
            for rclass, score in worker.resume.iteritems():
                skilled[rclass].remove((score, worker))
        else:
            _init_backlog(worker)
            workers.add(worker)
            self.nworkers = len(self.workers)
            self._update_decay()
            worker.lnode = self.unskilled.appendleft(worker)
            self.event.set()

        worker.resume = resume
        for rclass, score in resume.iteritems():
            try:
                skilled[rclass].add((score, worker))
            except KeyError:
                skilled[rclass] = set(((score, worker), ))

        logger.info('new resume\n%s', self)

    def remove(self, worker):
        skilled = self.skilled
        for rclass, score in worker.resume.iteritems():
            skilled[rclass].remove((score, worker))
        if getattr(worker, 'lnode', None) is not None:
            self.unskilled.remove(worker.lnode)
            worker.lnode = None
        self.workers.remove(worker)
        self.nworkers = len(self.workers)
        if self.nworkers:
            self._update_decay()
        else:
            self.event.clear()

    def get(self, rclass, timeout=None):
        """Get a worker to handle a request class
        """
        unskilled = self.unskilled
        if not unskilled:
            self.event.wait(timeout)
            if not unskilled:
                return None

        # Look for a skilled worker
        best_score = 0
        best_worker = None
        skilled = self.skilled.get(rclass)
        if skilled is None:
            skilled = self.skilled[rclass] = set()

        max_backlog = max(self.variance * self.mbacklog / self.nworkers, 1)
        for score, worker in skilled:
            if worker.mbacklog > max_backlog:
                continue
            backlog = worker.backlog + 1
            score /= backlog
            if (score > best_score):
                best_score = score
                best_worker = worker

        if not best_score:
            best_worker = unskilled.first.value
            if rclass not in best_worker.resume:
                # We now have an unskilled worker and we need to
                # assign it a score.
                score = self.unskilled_score
                best_worker.resume[rclass] = score
                skilled.add((score, best_worker))

        # Move worker from lru to mru end of queue
        unskilled.remove(best_worker.lnode)
        best_worker.lnode = unskilled.append(best_worker)

        best_worker.backlog += 1
        _decay_backlog(best_worker, self.worker_decay)

        self.backlog += 1
        _decay_backlog(self, self.decay)

        return best_worker

    def put(self, worker):
        self.backlog -= 1
        assert self.backlog >= 0, self.backlog
        _decay_backlog(self, self.decay)
        if worker.backlog > 0:
            worker.backlog -= 1
            _decay_backlog(worker, self.worker_decay)

def _init_backlog(worker):
    worker.backlog = worker.nbacklog = worker.dbacklog = worker.mbacklog = 0

def _decay_backlog(worker, decay):
    worker.dbacklog = worker.dbacklog*decay + worker.backlog
    worker.nbacklog = worker.nbacklog*decay + 1
    worker.mbacklog = worker.dbacklog / worker.nbacklog

class Worker(zc.resumelb.util.Worker):

    maxrno = (1<<32) - 1

    def __init__(self, pool, socket, addr):
        self.pool = pool
        self.nrequest = 0
        self.__name__ = '%s:%s' % addr

        readers = self.connected(socket, addr)

        while self.is_connected:
            try:
                rno, data = zc.resumelb.util.read_message(socket)
            except zc.resumelb.util.Disconnected:
                self.disconnected()
                return

            if rno == 0:
                pool.new_resume(self, data)
            else:
                try:
                    reader = readers[rno]
                except KeyError:
                    pass
                else:
                    reader(data)

    def __repr__(self):
        return self.__name__

    def handle(self, rclass, env, start_response):
        logger.debug('handled by %s', self.addr)

        env = env.copy()
        err = env.pop('wsgi.errors')
        input = env.pop('wsgi.input')
        env['zc.resumelb.request_class'] = rclass

        rno = self.nrequest + 1
        self.nrequest = rno % self.maxrno
        get = self.start(rno)
        try:
            self.put((rno, env))
            content_length = int(env.get('CONTENT_LENGTH', 0))
            while content_length > 0:
                data = input.read(min(content_length, block_size))
                if not data:
                    # Browser disconnected, cancel the request
                    self.put((rno, None))
                    self.end(rno)
                    return
                content_length -= len(data)
                self.put((rno, data))
            self.put((rno, ''))

            data = get()
            if data is None:
                raise zc.resumelb.util.Disconnected()
            logger.debug('start_response %r', data)
            start_response(*data)
        except:
            # not using finally here, because we only want to end on error
            self.end(rno)
            raise

        def content():
            try:
                while 1:
                    data = get()
                    if data:
                        logger.debug('yield %r', data)
                        yield data
                    else:
                        if data is None:
                            logger.warning('Disconnected while returning body')
                        break
            finally:
                self.end(rno)

        return content()

    def disconnected(self):
        self.pool.remove(self)
        zc.resumelb.util.Worker.disconnected(self)

def parse_addr(addr):
    host, port = addr.split(':')
    return host, int(port)

def host_classifier(env):
    host = env.get("HTTP_HOST", '')
    if host.startswith('www.'):
        return host[4:]
    return host

def re_classifier(name, regex):
    search = re.compile(regex).search

    def classifier(env):
        value = env.get(name)
        if value is not None:
            match = search(value)
            if match:
                return match.group('class')
        return ''

    return classifier

def main(args=None):
    """%prog [options] worker_addresses

    Run a resume-based load balancer on the give addresses.
    """
    if args is None:
        args = sys.argv[1:]

    import optparse
    parser = optparse.OptionParser(main.__doc__)
    parser.add_option(
        '-a', '--address', default=':0',
        help="Address to listed on for web requests"
        )
    parser.add_option(
        '-l', '--access-log', default='-',
        help='Access-log path.\n\n'
        'Use - (default) for standard output.\n'
        )
    parser.add_option(
        '-b', '--backlog', type='int',
        help="Server backlog setting.")
    parser.add_option(
        '-m', '--max-connections', type='int',
        help="Maximum number of simultanious accepted connections.")
    parser.add_option(
        '-L', '--logger-configuration',
        help=
        "Read logger configuration from the given configuration file path.\n"
        "\n"
        "The configuration file must be in ZConfig logger configuration syntax."
        )
    parser.add_option(
        '-r', '--request-classifier', default='zc.resumelb.lb:host_classifier',
        help="Request classification function (module:expr)"
        )
    parser.add_option(
        '-e', '--disconnect-message',
        help="Path to error page to use when a request is lost due to "
        "worker disconnection"
        )
    parser.add_option(
        '-v', '--variance', type='float', default=4.0,
        help="Maximum ration of a worker backlog to the mean backlog"
        )
    parser.add_option(
        '--backlog-history', type='int', default=9,
        help="Rough numner of requests to average worker backlogs over"
        )

    parser.add_option(
        '--unskilled-score', type='float', default=1.0,
        help="Score (requests/second) to assign to new workers."
        )

    options, args = parser.parse_args(args)
    if not args:
        print 'Error: must supply one or more worker addresses.'
        parser.parse_args(['-h'])

    if options.logger_configuration:
        logger_config = options.logger_configuration
        if re.match(r'\d+$', logger_config):
            logging.basicConfig(level=int(logger_config))
        elif logger_config in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
            logging.basicConfig(level=getattr(logging, logger_config))
        else:
            import ZConfig
            with open(logger_config) as f:
                ZConfig.configureLoggers(f.read())

    addrs = map(parse_addr, args)
    wsgi_addr = parse_addr(options.address)

    lb = LB(addrs, host_classifier,
            variance=options.variance,
            backlog_history=options.backlog_history,
            unskilled_score=options.unskilled_score)

    # Now, start a wsgi server
    addr = zc.parse_addr.parse_addr(options.address)
    if options.max_connections:
        spawn= gevent.pool.Pool(options.max_connections)
    else:
        spawn = 'default'

    accesslog = options.access_log
    if isinstance(accesslog, str):
        accesslog = sys.stdout if accesslog == '-' else open(accesslog, 'a')

    gevent.pywsgi.WSGIServer(
        wsgi_addr, lb.handle_wsgi, backlog = options.backlog,
        spawn = spawn, log = accesslog)

    gevent.pywsgi.WSGIServer(wsgi_addr, lb.handle_wsgi).serve_forever()


