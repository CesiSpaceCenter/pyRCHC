# A singleton is used to share an single class instance for all the application
# for example, we want to use a single logger object.
# with a singleton, we can initiate a new logger each time we need it,
# it will create a logger object if it doesn't exists, but after that it will use the same one

# https://stackoverflow.com/a/6798042
# https://python-patterns.guide/gang-of-four/singleton/

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:  # if the instance of this class has not been created yet
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)  # create it and store it in Singleton._instances
        return cls._instances[cls]  # return the created or found instance
