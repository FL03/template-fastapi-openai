


if __name__ == "__main__":
    from bftp.app import run
    import multiprocessing

    app = multiprocessing.Process(target=run)
    app.start()
