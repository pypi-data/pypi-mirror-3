import time
from progressbar import __version__ as pb_version, \
                        ProgressBar, Percentage, Bar, ETA

try:
    from progressbar import ProgressBarWidget
except ImportError:
    #API changed in 2.3
    from progressbar import Widget as ProgressBarWidget



class ETA_callback(ETA):
    """ProgressBarWidget for the Estimated Time of Arrival that
    call back a function when `seconds` or less left to arrival
    """
    def __init__(self, seconds=-1, callback=None):
        ETA.__init__(self)
        self._seconds = seconds
        self._callback = callback
        self._triggered = False

    def update(self, pbar):
        if pbar.currval == 0:
            return 'ETA:  --:--:--'
        elif pbar.finished:
            return 'Time: %s' % self.format_time(pbar.seconds_elapsed)
        else:
            elapsed = pbar.seconds_elapsed
            eta = elapsed * pbar.maxval / pbar.currval - elapsed
            if not self._triggered and eta <= self._seconds and self._callback:
                self._callback()
                self._triggered = True
            return 'ETA:  %s' % self.format_time(eta)


class LimitedFileTransferSpeed(ProgressBarWidget):
    """
    Widget for showing the transfer speed (useful for file transfers).
     It accepts an extra `max_rate` parameter (int in [kbps]) to limit
    (sleep) the download process when it is passed
    """

    def __init__(self, unit='B', max_rate=None):
        self.unit = unit
        self.fmt = '%6.2f %s'
        self.prefixes = ['', 'K', 'M', 'G', 'T', 'P']
        self.max_rate = max_rate

    def update(self, pbar):
        if pbar.seconds_elapsed < 2e-6:#== 0:
            bps = 0.0
        else:
            bps = pbar.currval / pbar.seconds_elapsed
            if self.max_rate:
                expected_time = pbar.currval / (float(self.max_rate) * 1024)
                sleep_time = expected_time - pbar.seconds_elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
        spd = bps
        for u in self.prefixes:
            if spd < 1024:
                break
            spd /= 1024
        return self.fmt % (spd, u + self.unit + '/s')
