import atexit
import inspect
import simplejson
import time
import warnings
import zmq

import fedmsg.json


class FedMsgContext(object):
    def __init__(self, **config):
        super(FedMsgContext, self).__init__()

        self.c = config

        # Prepare our context and publisher
        self.context = zmq.Context(config['io_threads'])
        method = config.get('active', False) or 'bind' and 'connect'
        method = ['bind', 'connect'][config['active']]

        # If no name is provided, use the calling module's __name__ to decide
        # which publishing endpoint to use.
        if not config.get("name", None):
            config["name"] = self.guess_calling_module()

            if config["name"] in ['__main__', 'fedmsg']:
                config["name"] = None

        # Actually set up our publisher
        if config.get("name", None) and config.get("endpoints", None):
            self.publisher = self.context.socket(zmq.PUB)

            if config['high_water_mark']:
                self.publisher.setsockopt(zmq.HWM, config['high_water_mark'])

            # Call either bind or connect on the new publisher
            getattr(self.publisher, method)(config["endpoints"][config["name"]])
        else:
            # fedmsg is not configured to send any messages
            #raise ValueError("FedMsgContext was misconfigured.")
            pass

        # Define and register a 'destructor'.
        def destructor():
            if hasattr(self, 'publisher'):
                self.publisher.close()

            self.context.term()

        atexit.register(destructor)

        # Sleep just to make sure that the socket gets set up before anyone
        # tries anything.  This is a documented zmq 'feature'.
        time.sleep(config['post_init_sleep'])

    def subscribe(self, topic, callback):
        raise NotImplementedError

    # TODO -- this should be in kitchen, not fedmsg
    def guess_calling_module(self):
        # Iterate up the call-stack and return the first new top-level module
        for frame in (f[0] for f in inspect.stack()):
            modname = frame.f_globals['__name__'].split('.')[0]
            if modname != "fedmsg":
                return modname

        # Otherwise, give up and just return out own module name.
        return "fedmsg"

    def send_message(self, topic=None, msg=None, modname=None, validate=True):

        if not topic:
            warnings.warn("Attempted to send message with no topic.  Bailing.")
            return

        if not msg:
            warnings.warn("Attempted to send message with no msg.  Bailing.")
            return

        # If no modname is supplied, then guess it from the call stack.
        modname = modname or self.guess_calling_module()

        topic = '.'.join([self.c['environment'], modname, topic])

        if topic[:len(self.c['topic_prefix'])] != self.c['topic_prefix']:
            topic = self.c['topic_prefix'] + '.' + topic

        msg = dict(topic=topic, msg=msg, timestamp=time.time())

        self.publisher.send_multipart([topic, fedmsg.json.dumps(msg)])

    def have_pulses(self, endpoints):
        """
        Returns a dict of endpoint->bool mappings indicating which endpoints
        are emitting detectable heartbeats.
        """

        topic = self.c['topic_prefix'] + '.heartbeat'

        # TODO - include endpoint name in the results dict
        results = dict(zip(endpoints.values(), [False] * len(endpoints)))
        tic = time.time()

        generator = self._tail_messages(
            endpoints, topic, timeout=self.c['timeout'])

        for name, ep, topic, msg in generator:
            results[ep] = True
            if all(results.values()) or (time.time() - tic) < self.c['timeout']:
                break

        return results

    def _tail_messages(self, endpoints, topic="", passive=False, **kw):
        """
        Generator that yields messages on the bus in the form of tuples::

        >>> (endpoint, topic, message)
        """

        # TODO -- the 'passive' here and the 'active' are ambiguous.  They don't
        # actually mean the same thing.
        method = passive and 'bind' or 'connect'

        subs = {}
        for _name, endpoint in endpoints.iteritems():
            subscriber = self.context.socket(zmq.SUB)
            subscriber.setsockopt(zmq.SUBSCRIBE, topic)
            getattr(subscriber, method)(endpoint)
            subs[endpoint] = subscriber

        timeout = kw['timeout']
        tic = time.time()
        try:
            while True:
                for _name, e in endpoints.iteritems():
                    try:
                        _topic, message = subs[e].recv_multipart(zmq.NOBLOCK)
                        tic = time.time()
                        yield _name, e, _topic, fedmsg.json.loads(message)
                    except zmq.ZMQError:
                        if timeout and (time.time() - tic) > timeout:
                            return
        finally:
            for _name, endpoint in endpoints.iteritems():
                subs[endpoint].close()
