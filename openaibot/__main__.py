from . import init


def main():
    app = init()
    app.run_polling()


if __name__ == '__main__':
    main()
