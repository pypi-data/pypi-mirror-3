#
# Copyright (c) 2006-2012, Prometheus Research, LLC
#


from ...core.domain import PGDomain
from htsql.tweak.inet.domain import INetDomain


class PGINetDomain(PGDomain, INetDomain):
    pass


