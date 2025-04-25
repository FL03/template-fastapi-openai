if __name__ == "__main__":
    from bftp.app import run
    import multiprocessing

    app = multiprocessing.Process(target=run)
    # start the application in a separate process
    app.start()
    # wait for the application to finish
    app.join()
