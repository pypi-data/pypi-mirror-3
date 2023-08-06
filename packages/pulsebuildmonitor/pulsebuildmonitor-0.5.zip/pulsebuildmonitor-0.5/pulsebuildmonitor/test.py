from factory import start_pulse_monitor

def unittest_callback(data):
    print 'unittest_callback', data

def build_callback(data):
    print 'build_callback', data


if __name__ == "__main__":
    m = start_pulse_monitor(talos=True,
                            testCallback=unittest_callback,
                            buildCallback=build_callback)
    m.join()
