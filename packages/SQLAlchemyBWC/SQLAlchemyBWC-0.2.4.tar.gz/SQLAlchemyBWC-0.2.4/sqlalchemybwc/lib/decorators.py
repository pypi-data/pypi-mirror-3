"""
    It is expected that most of these decorators will be used on entity class
    methods.  When using them on a regular function, use the decorator with the
    "ncm" postfix:

        ncm => Non-Class Method
"""
import inspect

from decorator import decorator
from sqlalchemy.orm.exc import NoResultFound

from compstack.sqlalchemy import db
from compstack.sqlalchemy.lib.helpers import is_unique_exc

def _find_sa_sess(args):
    """
        The decorators will by default use sqlalchemy.db to find the SQLAlchemy
        session.  However, if the function being decorated is a method of a
        a class and that class has a _sa_sess() method, it will be called
        to retrieve the SQLAlchemy session that should be used.

        This function determins where the SA session is.
    """
    # If the function being decorated is a classmethod, and the class
    # has an attribute _sa_sess,
    if args and inspect.isclass(args[0]) and hasattr(args[0], '_sa_sess'):
        return args[0]._sa_sess()
    return db.sess

@decorator
def transaction_ncm(f, *args, **kwargs):
    """
        decorates a function so that a DB transaction is always committed after
        the wrapped function returns and also rolls back the transaction if
        an unhandled exception occurs.

        'ncm' = non class method (version)
    """
    dbsess = _find_sa_sess(args)

    try:
        retval = f(*args, **kwargs)
        dbsess.commit()
        return retval
    except Exception:
        dbsess.rollback()
        raise

def transaction(f):
    """
        like transaction_ncm() but makes the function a class method
    """
    return classmethod(transaction_ncm(f))

@decorator
def ignore_unique_ncm(f, *args, **kwargs):
    """
        Ignores exceptions caused by unique constraints or
        indexes in the wrapped function.

        'ncm' = non class method (version)
    """
    dbsess = _find_sa_sess(args)
    try:
        return f(*args, **kwargs)
    except Exception, e:
        dbsess.rollback()
        if is_unique_exc(e):
                return
        raise

def ignore_unique(f):
    """
        like ignore_unique_ncm() but makes the decorated function a class method
    """
    return classmethod(ignore_unique_ncm(f))

@decorator
def one_to_none_ncm(f, *args, **kwargs):
    """
        wraps a function that uses SQLAlahcemy's ORM .one() method and returns
        None instead of raising an exception if there was no record returned.
        If multiple records exist, that exception is still raised.
    """
    try:
        return f(*args, **kwargs)
    except NoResultFound, e:
        if 'No row was found for one()' != str(e):
            raise
        return None

def one_to_none(f):
    """
        like one_to_none_ncm() but makes the decorated function a class method
    """
    return classmethod(one_to_none_ncm(f))
