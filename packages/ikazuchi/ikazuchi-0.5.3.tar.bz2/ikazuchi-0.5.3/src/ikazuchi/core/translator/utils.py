# -*- coding: utf-8 -*-

import threading

_MAX_SEMAPHORE = 10

def call_api_with_multithread(api_method, target_lines):
    def worker(line, results, i, semaphore):
        with semaphore:
            results[i] = api_method(line)

    results = [("", "")] * len(target_lines)
    s = threading.Semaphore(_MAX_SEMAPHORE)
    for i, line in enumerate(target_lines):
        if line:
            t = threading.Thread(target=worker, args=(line, results, i, s))
            t.start()
    # waiting for threads to complete
    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()
    return results

def get_ip_address():
    import socket
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except:
        ip = "127.0.0.1"
    return ip
