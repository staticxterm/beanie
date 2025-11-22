from pymongo.asynchronous.client_session import AsyncClientSession


class SessionMethods:
    """
    Session methods
    """

    def set_session(self, session: AsyncClientSession | None = None):
        """
        Set session.

        :param session: PyMongo session
        :return: Query instance
        :rtype: Self
        """
        if session is not None:
            self.session: AsyncClientSession | None = session
        return self
