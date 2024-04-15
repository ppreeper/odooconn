import logging
import xmlrpc.client

logger = logging.getLogger(__name__)


class OdooConn:
    def __init__(self, config):
        self.hostname = config.get("hostname")
        self.port = config.get("port")
        self.schema = config.get("schema")
        self.database = config.get("database")
        self.username = config.get("username")
        self.password = config.get("password")
        self.url = config.get("url")
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        self.uid = self.common.authenticate(
            self.database, self.username, self.password, {}
        )

    def create(self, model: str, values: list):
        """
        Create a single record for the model and return its id

        model: model name
        values: list of field values

        Example:
        values = {
            "name": "ZExample1",
            "email": "zexample1@example.com",
        }
        """
        try:
            return self.models.execute_kw(
                self.database, self.uid, self.password, model, "create", [values]
            )
        except xmlrpc.client.Fault as err:
            logger.error("err={} model={} values={}".format(err, model, values))

    def load(self, model: str, header: list, values: list):
        """
        Create multiple records using a datamatrix and return their ids

        model: model name
        header: list of field names
        values: list of lists of field values

        Example:
        header = ["name", "email"]
        values = [
            ["ZExample1", "zexample1@example.com"],
            ["ZExample2", "zexample1@example.com"],
            ]
        """
        try:
            return self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                model,
                "load",
                [[header], [values]],
            )
        except xmlrpc.client.Fault as err:
            logger.error("err={} model={} values={}".format(err, model, values))

    def count(self, model: str, domain, limit: int = 0):
        """
        Returns the number of record in the current model
        matching the :domain with a maximum of :limit records

        model: model name
        domain: list of search criteria following the modified odoo domain syntax
        limit: maximum number of records to return

        Example:
        domain = [[["name", "=", "ZExample1"]]]
        limit = 1
        """
        return self.models.execute_kw(
            self.database,
            self.uid,
            self.password,
            model,
            "search_count",
            domain,
            {"limit": limit},
        )

    def fields_get(self, model: str, attributes: list):
        """
        Returns the definition of the fields of the model

        model: model name
        attributes: list of field attributes to return

        Example:
        attributes = ["string", "help", "type"]
        """
        if not attributes:
            return self.models.execute_kw(
                self.database, self.uid, self.password, model, "fields_get", []
            )
        else:
            return self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                model,
                "fields_get",
                [],
                {"attributes": attributes},
            )

    def get_id(self, model: str, domain):
        """
        Return id of the first record matching the query, or -1 if none is found

        model: model name
        domain: list of search criteria following the modified odoo domain syntax

        Example:
        domain = [[["name", "=", "ZExample1"]]]
        """
        id = self.models.execute_kw(
            self.database,
            self.uid,
            self.password,
            model,
            "search",
            domain,
            {"limit": 1},
        )
        return id[0] if id else -1

    def search(self, model: str, domain):
        """
        Return ids of records matching the query

        model: model name
        domain: list of search criteria following the modified odoo domain syntax

        Example:
        domain = [[["name", "=", "ZExample1"]]]
        """
        return self.models.execute_kw(
            self.database, self.uid, self.password, model, "search", domain
        )

    def read(self, model: str, ids: list, fields: list):
        """
        Read the requested fields of the records with the given ids

        model: model name
        ids: list of record ids
        fields: list of field names

        Example:
        ids = [1, 2, 3]
        fields = ["name", "email"]

        """
        return self.models.execute_kw(
            self.database,
            self.uid,
            self.password,
            model,
            "read",
            [ids],
            {"fields": fields},
        )

    def search_read(
        self, model: str, domain, offset: int = 0, limit: int = 0, fields: list = []
    ):
        """
        Return the requested fields of the records matching the query

        model: model name
        domain: list of search criteria following the modified odoo domain syntax
        offset: number of records to skip
        limit: maximum number of records to return
        fields: list of field names

        Example:
        domain = [[["name", "=", "ZExample1"]]]
        offset = 0
        limit = 1
        fields = ["name", "email"]
        """
        try:
            return self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                model,
                "search_read",
                domain,
                {"offset": offset, "limit": limit, "fields": fields},
            )
        except xmlrpc.client.Fault as err:
            logger.error("err={} model={} values={}".format(err, model))

    def write(self, model: str, id: int, values: list):
        """
        Update all the fields of the records with the given ids with the provided values

        model: model name
        id: record id
        values: list of field values

        Example:
        id = 1
        values = {
            "name": "ZExample1",
            "email": "zexample1_1@example.com",
        }
        """
        try:
            return self.models.execute_kw(
                self.database, self.uid, self.password, model, "write", [[id], values]
            )
        except xmlrpc.client.Fault as err:
            logger.error(
                "err={} model={} id={} values={}".format(err, model, id, values)
            )

    def unlink(self, model: str, ids: list):
        """
        Delete the records with the given ids

        model: model name
        ids: list of record ids

        Example:
        ids = [1, 2, 3]
        """
        return self.models.execute_kw(
            self.database, self.uid, self.password, model, "unlink", [ids]
        )

    def execute(self, model: str, method: str, args):
        """
        call a method of the model

        model: model name
        method: method name
        args: list of arguments

        Example:
        model = "res.partner"
        method = "search_read"
        """
        return self.models.execute_kw(
            self.database, self.uid, self.password, model, method, args
        )

    def execute_kw(self, model: str, method: str, args, kwargs):
        """
        call a method of the model

        model: model name
        method: method name
        args: list of arguments
        kwargs: dictionary of keyword arguments

        Example:
        model = "res.partner"
        method = "search_read"
        """
        return self.models.execute_kw(
            self.database, self.uid, self.password, model, method, args, kwargs
        )
