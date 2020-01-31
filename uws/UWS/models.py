# -*- coding: utf-8 -*-
from __future__ import print_function

import six
from lxml import etree as et


UWS_1_NAMESPACE = "http://www.ivoa.net/xml/UWS/v1.0"
#UWS_2_NAMESPACE = "http://www.ivoa.net/xml/UWS/v2.0"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"


class UWS1Flavour:
    def __init__(self, namespaces=None):

        if UWS_1_NAMESPACE not in namespaces.values():
            raise RuntimeError("No supported UWS namespace found in xml-response, "
                               "cannot parse xml.")

        # prepend each element's name with the correct uws-namespace
        # for this version
        self.uws_namespace = UWS_1_NAMESPACE
        self.jobs = et.QName(self.uws_namespace, "jobs")
        self.jobref = et.QName(self.uws_namespace, "jobref")
        self.phase = et.QName(self.uws_namespace, "phase")
        self.job_id = et.QName(self.uws_namespace, "jobId")
        self.run_id = et.QName(self.uws_namespace, "runId")
        self.owner_id = et.QName(self.uws_namespace, "ownerId")
        self.quote = et.QName(self.uws_namespace, "quote")
        self.creation_time = et.QName(self.uws_namespace, "creationTime")
        self.start_time = et.QName(self.uws_namespace, "startTime")
        self.end_time = et.QName(self.uws_namespace, "endTime")
        self.execution_duration = et.QName(self.uws_namespace, "executionDuration")
        self.destruction = et.QName(self.uws_namespace, "destruction")
        self.parameters = et.QName(self.uws_namespace, "parameters")
        self.results = et.QName(self.uws_namespace, "results")
        self.error_summary = et.QName(self.uws_namespace, "errorSummary")
        self.message = et.QName(self.uws_namespace, "message")
        self.job_info = et.QName(self.uws_namespace, "jobInfo")


class JobPhases:
    COMPLETED = 'COMPLETED'
    PENDING = 'PENDING'
    QUEUED = 'QUEUED'
    EXECUTING = 'EXECUTING'
    ERROR = 'ERROR'
    ABORTED = 'ABORTED'
    UNKNOWN = 'UNKNOWN'
    HELD = 'HELD'
    SUSPENDED = 'SUSPENDED'
    ARCHIVED = 'ARCHIVED'

    phases = [COMPLETED, PENDING, QUEUED, EXECUTING,
              ERROR, ABORTED, UNKNOWN, HELD,
              SUSPENDED, ARCHIVED]

    # phases for which blocking behaviour can occur:
    active_phases = [PENDING, QUEUED, EXECUTING]

    versions = {
        COMPLETED: ['1.0', '1.1'],
        PENDING: ['1.0', '1.1'],
        QUEUED: ['1.0', '1.1'],
        EXECUTING: ['1.0', '1.1'],
        ERROR: ['1.0', '1.1'],
        ABORTED: ['1.0', '1.1'],
        UNKNOWN: ['1.0', '1.1'],
        HELD: ['1.0', '1.1'],
        SUSPENDED: ['1.0', '1.1'],
        ARCHIVED: ['1.1']
    }


class BaseUWSModel:
    def __init__(self):
        self.version = "1.0"

    @staticmethod
    def _parse_bool(value):
        if isinstance(value, str):
            if value.lower() == 'true':
                return True
            return False
        return value

class Jobs(BaseUWSModel):
    def __init__(self, xml=None):
        super(Jobs, self).__init__()

        self.job_reference = None

        if xml is not None:
            # parse xml
            if isinstance(xml, bytes):
                parsed = et.fromstring(xml.decode())
            else:
                parsed = et.fromstring(xml.encode('utf-8'))

            uws_flavour = UWS1Flavour(parsed.nsmap)

            if parsed.get("version"):
                self.version = parsed.get("version")

            xml_jobs = parsed.findall(uws_flavour.jobref)

            self.job_reference = []

            for xml_job in xml_jobs:
                self.add_job(job=JobRef(xml_node=xml_job,
                                        xml_namespace=parsed.nsmap,
                                        uws_flavour=uws_flavour))
        else:
            self.job_reference = []

    def __unicode__(self):
        strng = ""
        for job in self.job_reference:
            strng += str(job) + "\n"
        return strng

    def __str__(self):
        return str(self.__unicode__())
        #  return unicode(self).encode('utf-8')

    def add_job(self, jid=None, href=None, phase=None, job=None):
        if job is not None:
            self.job_reference.append(job)
        else:
            reference = Reference(href=href, rtype="simple")
            job_reference = JobRef(jid=jid, phase=phase, reference=reference)
            self.job_reference.append(job_reference)


class JobRef(BaseUWSModel):
    def __init__(self, jid=None, phase=None, reference=None, xml_node=None, xml_namespace=None,
                 uws_flavour=None):
        super(JobRef, self).__init__()

        self.jid = None
        self.reference = Reference()
        self.phase = []

        if xml_node is not None:  # When should this ever be None?????
            self.jid = xml_node.get('id')

            # UWS standard defines array, therefore treat phase as array
            # (... actually it does not, but keep it anyway like this, maybe at
            # some point in the future all phases of a job are provided as list)
            self.phase = [elm.text for elm in xml_node.findall(uws_flavour.phase)]
            self.reference = Reference(xml_node=xml_node, xml_namespace=xml_namespace)
            self.run_id = xml_node.get('runId')
            self.owner_id = xml_node.get('ownerId')
            self.creation_time = xml_node.get('creationTime')

        elif jid is not None and phase is not None and reference is not None:
            self.jid = jid

            if isinstance(phase, six.string_types):
                self.phase = [phase]
            else:
                self.phase = phase

            if isinstance(reference, Reference):
                self.reference = reference
            else:
                raise RuntimeError("Malformated reference given in jobref id: %s" % jid)

    def set_phase(self, new_phase):
        self.phase = [new_phase]

    def __unicode__(self):
        if self.creation_time is not None:
            return "Job '%s' in phase '%s' created at '%s' - %s" % (self.jid,
                                                                    ', '.join(self.phase),
                                                                    self.creation_time,
                                                                    str(self.reference))
        else:
            return "Job '%s' in phase '%s' - %s" % (self.jid, ', '.join(self.phase),
                                                    str(self.reference))

    def __str__(self):
        return str(self.__unicode__())


class Reference(BaseUWSModel):
    def __init__(self, href=None, rtype=None, xml_node=None, xml_namespace=None):
        super(Reference, self).__init__()

        self.type = "simple"
        self.href = ""

        if xml_node is not None:
            # check that namespace for xlink really exists
            if XLINK_NAMESPACE not in xml_namespace.values():
                raise RuntimeError("No supported xlink namespace found in xml-response, "
                                   "cannot parse xml.")

            qualifiedname_type = et.QName(XLINK_NAMESPACE, "type")
            qualifiedname_href = et.QName(XLINK_NAMESPACE, "href")
            self.type = xml_node.get(qualifiedname_type)
            self.href = xml_node.get(qualifiedname_href)
        elif href is not None and rtype is not None:
            self.type = rtype
            self.href = href

    def __unicode__(self):
        return self.href

    def __str__(self):
        return str(self.__unicode__())


class Job(BaseUWSModel):
    def __init__(self, xml=None):
        super(Job, self).__init__()

        self.job_id = None
        self.run_id = None
        self.owner_id = None
        self.phase = ["PENDING"]
        self.quote = None
        self.creation_time = None
        self.start_time = None
        self.end_time = None
        self.execution_duration = 0
        self.destruction = None
        self.parameters = []
        self.results = []
        self.error_summary = None
        self.job_info = []

        if xml is not None:
            # parse xml
            try:
                xml = xml.decode()
            except AttributeError:
                pass

            parsed = et.fromstring(xml.encode('utf-8'))

            # again find proper UWS namespace-string as prefix for search paths in find
            uws_flavour = UWS1Flavour(parsed.nsmap)

            if parsed.get("version"):
                self.version = parsed.get("version")

            self.job_id = self._get_mandatory(parsed, uws_flavour.job_id)
            self.run_id = self._get_optional(parsed, uws_flavour.run_id)
            self.owner_id = self._get_optional(parsed, uws_flavour.owner_id)
            self.phase = [self._get_mandatory(parsed, uws_flavour.phase)]
            self.quote = self._get_optional(parsed, uws_flavour.quote)
            self.creation_time = self._get_optional(parsed, uws_flavour.creation_time)
            self.start_time = self._get_mandatory(parsed, uws_flavour.start_time)
            self.end_time = self._get_mandatory(parsed, uws_flavour.end_time)
            self.execution_duration = int(self._get_mandatory(parsed,
                                                              uws_flavour.execution_duration))
            self.destruction = self._get_mandatory(parsed, uws_flavour.destruction)

            self.parameters = []
            tmp = parsed.find(uws_flavour.parameters)
            if tmp is not None:
                parameters = list(tmp)
            for param in parameters:
                self.add_parameter(parameter=Parameter(xml_node=param))

            self.results = []
            tmp = parsed.find(uws_flavour.results)
            if tmp is not None:
                results = list(tmp)
            for res in results:
                self.add_result(result=Result(xml_node=res, xml_namespace=parsed.nsmap))

            self.error_summary = False
            tmp = parsed.find(uws_flavour.error_summary)
            if tmp is not None:
                self.error_summary = ErrorSummary(xml_node=tmp, uws_flavour=uws_flavour)

            self.job_info = []
            tmp = parsed.find(uws_flavour.job_info)
            if tmp is not None:
                self.job_info = list(tmp)

    def __unicode__(self):
        strng = "JobId : '%s'\n" % self.job_id
        strng += "RunId : '%s'\n" % self.run_id
        strng += "OwnerId : '%s'\n" % self.owner_id
        strng += "Phase : '%s'\n" % ', '.join(self.phase)
        strng += "Quote : '%s'\n" % self.quote
        strng += "CreationTime : '%s'\n" % self.creation_time
        strng += "StartTime : '%s'\n" % self.start_time
        strng += "EndTime : '%s'\n" % self.end_time
        strng += "ExecutionDuration : '%s'\n" % self.execution_duration
        strng += "Destruction : '%s'\n" % self.destruction

        strng += "Parameters :\n"
        for param in self.parameters:
            strng += "%s\n" % str(param)

        strng += "Results :\n"
        for res in self.results:
            strng += "%s\n" % str(res)

        strng += "errorSummary :\n %s\n" % str(self.error_summary)

        strng += "jobInfo :\n"
        for info in self.job_info:
            strng += "%s\n" % str(info)

        return strng

    def __str__(self):
        return str(self.__unicode__())
        #  return unicode(self).encode('utf-8')

    def add_parameter(self, pid=None, by_reference=False, is_post=False, value=None,
                      parameter=None):
        if not parameter:
            parameter = Parameter(pid=pid, by_reference=by_reference, is_post=is_post, value=value)

        self.parameters.append(parameter)

    def add_result(self, rid=None, href=None, result=None):
        if not result:
            reference = Reference(href=href, rtype="simple")
            result = Result(rid=rid, reference=reference)

        self.results.append(result)

    @staticmethod
    def _get_optional(parsed, element_name):
        """Returns the text value of element_name within the parsed elementTree.

        If element_name doesn't exist, return None.
        """
        option = parsed.find(element_name)
        if option is None:
            return None
        else:
            return option.text

    @staticmethod
    def _get_mandatory(parsed, element_name):
        """Check if the element exists, return text or error"""

        element = parsed.find(element_name)
        if element is None:
            raise RuntimeError("Mandatory element ", element_name.text,
                               " could not be found in xml-response.")
        else:
            return element.text


class Parameter(BaseUWSModel):
    def __init__(self, pid=None, by_reference=False, is_post=False, value=None, xml_node=None):
        super(Parameter, self).__init__()

        self.pid = None
        self.by_reference = False
        self.is_post = False
        self.value = None

        if xml_node is not None:
            self.pid = xml_node.get('id')
            self.by_reference = self._parse_bool(xml_node.get('by_reference', default=False))
            self.is_post = self._parse_bool(xml_node.get('is_post', default=False))
            self.value = xml_node.text
        elif pid is not None and value is not None:
            self.pid = pid
            self.by_reference = by_reference
            self.is_post = is_post
            self.value = value

    def __unicode__(self):
        return "Parameter id '%s' byRef: %s is_post: %s - value: %s" % (self.pid, self.by_reference,
                                                                        self.is_post, self.value)

    def __str__(self):
        return str(self.__unicode__())


class Result(BaseUWSModel):
    def __init__(self, rid=None, reference=None, xml_node=None, xml_namespace=None):
        super(Result, self).__init__()

        self.rid = None
        self.reference = Reference()

        if xml_node is not None:
            self.rid = xml_node.get('id')
            self.reference = Reference(xml_node=xml_node, xml_namespace=xml_namespace)
        elif rid is not None and reference is not None:
            self.rid = rid

            if isinstance(reference, Reference):
                self.reference = reference
            else:
                raise RuntimeError("Malformated reference given in result id: %s" % rid)

    def __unicode__(self):
        return "Result id '%s' reference: %s" % (self.rid, str(self.reference))

    def __str__(self):
        return str(self.__unicode__())


class ErrorSummary(BaseUWSModel):
    def __init__(self, etype="transient", has_detail=False, messages=None,
                 xml_node=None, uws_flavour=None):
        super(ErrorSummary, self).__init__()

        self.type = "transient"
        self.has_detail = False
        self.messages = []

        if xml_node is not None:
            self.type = xml_node.get('type')
            self.has_detail = self._parse_bool(xml_node.get('hasDetail', default=False))

            self.messages = []
            messages = xml_node.findall(uws_flavour.message)

            for message in messages:
                self.messages.append(message.text)

        elif messages is not None:
            self.type = etype
            self.has_detail = has_detail
            self.messages = messages

    def __unicode__(self):
        return "Error Summary - type '%s' hasDetail: %s - message: %s" % (self.type,
                                                                          self.has_detail,
                                                                          "\n".join(self.messages))

    def __str__(self):
        return str(self.__unicode__())
