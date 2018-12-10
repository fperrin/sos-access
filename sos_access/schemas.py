import marshmallow
from marshmallow.validate import Length, OneOf
import xmltodict

ALLOWED_STATUS_CODES = [0, 1, 2, 3, 4, 5, 7, 9, 10, 99, 100, 101]

# TODO: write tests for all schemas.

class SOSAccessRequest:
    pass


class AlarmRequest(SOSAccessRequest):

    def __init__(self, event_code, transmitter_type, transmitter_code,
                 authentication, receiver, alarm_type=None,
                 transmitter_time=None, reference=None, transmitter_area=None,
                 section=None, section_text=None, detector=None,
                 detector_text=None, additional_info=None, position=None):
        self.event_code = event_code
        self.transmitter_type = transmitter_type
        self.transmitter_code = transmitter_code
        self.authentication = authentication
        self.receiver = receiver
        self.alarm_type = alarm_type
        self.transmitter_time = transmitter_time
        self.reference = reference
        self.transmitter_area = transmitter_area
        self.section = section
        self.section_text = section_text
        self.detector = detector
        self.detector_text = detector_text
        self.additional_info = additional_info
        self.position = position

    def __repr__(self):
        # TODO: better repr!
        return f'{self.__class__}(event_code={self.event_code})'


class AlarmResponse(SOSAccessRequest):

    def __init__(self, status, info, arrival_time=None, reference=None):
        self.reference = reference
        self.status = status
        self.info = info
        self.arrival_time = arrival_time


class NewAuthRequest(SOSAccessRequest):

    def __init__(self, authentication, transmitter_code, transmitter_type,
                 reference=None):
        self.authentication = authentication
        self.reference = reference
        self.transmitter_code = transmitter_code
        self.transmitter_type = transmitter_type


class NewAuthResponse(SOSAccessRequest):

    def __init__(self, status, info, new_authentication, reference=None):
        self.reference = reference
        self.status = status
        self.info = info
        self.new_authentication = new_authentication


class PingRequest(SOSAccessRequest):

    def __init__(self, authentication, transmitter_code, transmitter_type,
                 reference=None):
        self.authentication = authentication
        self.reference = reference
        self.transmitter_code = transmitter_code
        self.transmitter_type = transmitter_type


class PingResponse(SOSAccessRequest):
    def __init__(self, status, info, arrival_time=None, reference=None):
        self.reference = reference
        self.status = status
        self.info = info
        self.arrival_time = arrival_time  # Alarm Request


class PositionSchema(marshmallow.Schema):
    """
    <pos> Geographical coordinate in the format
    RT90 (2,5 gon West):
    “xXXXXXXXyYYYYYYY”

    where x is the x-coordinate, y is the y-
    coordinate. Values are given in meters.

    Ex. ”x1234567y1234567”.

    or in the format WGS84 (Lat/Long):
    “NDDMMmmEDDDMMmm”
    where DD are degrees; MM minutes; mm
    decimal minutes (leading 0 shall be given on
    the longitude if needed).

    ex WGS84
    <position>
    <pos>E597295E0176288</pos>
    </position>
    Ex RT90
    <position>
    <pos>x1234567y1234567</pos>
    <position>
    """
    pos = marshmallow.fields.String(required=True,
                                    validate=[Length(min=14, max=16)])

    class Meta:
        ordered = True


class SOSAccessSchema(marshmallow.Schema):
    __envelope__ = None
    __model__ = None

    @marshmallow.pre_load()
    def load_xml(self, data):
        # incoming XML
        parsed_data = xmltodict.parse(data)
        # remove envelope
        return parsed_data[self.__envelope__]

    @marshmallow.post_dump()
    def dump_xml(self, data):
        # add the envelope
        data_to_dump = {self.__envelope__: data}
        # make xml
        return xmltodict.unparse(data_to_dump)

    @marshmallow.post_load()
    def make_object(self, data):
        return self.__model__(**data)


class AlarmRequestSchema(SOSAccessSchema):
    __envelope__ = 'alarmrequest'
    __model__ = AlarmRequest

    reference = marshmallow.fields.String(allow_none=True,
                                          validate=[Length(min=1, max=50)])
    authentication = marshmallow.fields.String(required=True,
                                               validate=[Length(equal=15)])
    receiver = marshmallow.fields.String(required=True,
                                         validate=[Length(min=1, max=20)])
    transmitter_time = marshmallow.fields.DateTime(allow_none=True,
                                                   data_key='transmittertime')
    alarm_type = marshmallow.fields.String(allow_none=True,
                                           validate=[Length(min=1, max=2)],
                                           data_key='alarmtype')
    transmitter_type = marshmallow.fields.String(required=True,
                                                 validate=[Length(equal=5)],
                                                 data_key='transmittertype')
    transmitter_code = marshmallow.fields.String(required=True, validate=[
        Length(min=1, max=15)], data_key='transmittercode')
    transmitter_area = marshmallow.fields.String(allow_none=True, validate=[
        Length(min=1, max=5)], data_key='transmitterarea')
    event_code = marshmallow.fields.String(required=True,
                                           validate=[Length(min=1, max=25)],
                                           data_key='eventcode')
    section = marshmallow.fields.String(allow_none=True,
                                        validate=[Length(min=1, max=5)])
    section_text = marshmallow.fields.String(allow_none=True,
                                             validate=[Length(min=1, max=40)],
                                             data_key='sectionkey')
    detector = marshmallow.fields.String(allow_none=True,
                                         validate=[Length(min=1, max=5)])
    detector_text = marshmallow.fields.String(allow_none=True,
                                              validate=[Length(min=1, max=40)],
                                              data_key='detectortext')
    # Lines in additionalinfo is separated via CR+LF or LF. CR = 0x0a LF = 0x0d
    additional_info = marshmallow.fields.String(allow_none=True, validate=[
        Length(min=1, max=2000)], data_key='additinalinfo')

    position = marshmallow.fields.Nested(PositionSchema, allow_none=True)

    class Meta:
        ordered = True


# Alarm Response


class AlarmResponseSchema(SOSAccessSchema):
    __envelope__ = 'alarmresponse'
    __model__ = AlarmResponse

    reference = marshmallow.fields.String(allow_none=True,
                                          validate=[Length(min=1, max=50)])
    status = marshmallow.fields.Integer(required=True,
                                        validate=[OneOf(ALLOWED_STATUS_CODES)])
    info = marshmallow.fields.String(required=True,
                                     validate=[Length(min=1, max=255)])
    arrival_time = marshmallow.fields.DateTime(allow_none=True,
                                               data_key='arrivaltime', format='rfc')

    class Meta:
        ordered = True


# Request new authentication

class NewAuthRequestSchema(SOSAccessSchema):
    __envelope__ = 'requestnewauthentication'
    __model__ = NewAuthRequest

    authentication = marshmallow.fields.String(required=True,
                                               validate=[Length(equal=15)])
    reference = marshmallow.fields.String(allow_none=True,
                                          validate=[Length(min=1, max=50)])
    transmitter_code = marshmallow.fields.String(required=True, validate=[
        Length(min=1, max=15)], data_key='transmittercode')
    transmitter_type = marshmallow.fields.String(required=True,
                                                 validate=[Length(equal=5)],
                                                 data_key='transmittertype')

    class Meta:
        ordered = True


# Request new authentication response


class NewAuthResponseSchema(SOSAccessSchema):
    __envelope__ = 'requestnewauthenticationresponse'
    __model__ = NewAuthResponse

    reference = marshmallow.fields.String(allow_none=True,
                                          validate=[Length(min=1, max=50)])
    status = marshmallow.fields.Integer(required=True,
                                        validate=[OneOf(ALLOWED_STATUS_CODES)])
    info = marshmallow.fields.String(required=True,
                                     validate=[Length(min=1, max=255)])
    new_authentication = marshmallow.fields.String(required=True,
                                                   validate=[Length(equal=15)],
                                                   data_key='newauthentication')

    class Meta:
        ordered = True


# Ping request


class PingRequestSchema(SOSAccessSchema):
    __envelope__ = 'pingrequest'
    __model__ = PingRequest

    authentication = marshmallow.fields.String(required=True,
                                               validate=[Length(equal=15)])
    reference = marshmallow.fields.String(allow_none=True,
                                          validate=[Length(min=1, max=50)])
    transmitter_code = marshmallow.fields.String(required=True, validate=[
        Length(min=1, max=15)], data_key='transmittercode')
    transmitter_type = marshmallow.fields.String(required=True,
                                                 validate=[Length(equal=5)],
                                                 data_key='transmittertype')

    class Meta:
        ordered = True


# Ping response


class PingResponseSchema(SOSAccessSchema):
    __envelope__ = 'pingresponse'
    __model__ = PingResponse

    reference = marshmallow.fields.String(allow_none=True,
                                          validate=[Length(min=1, max=50)])
    status = marshmallow.fields.Integer(required=True,
                                        validate=[OneOf(ALLOWED_STATUS_CODES)])
    info = marshmallow.fields.String(required=True,
                                     validate=[Length(min=1, max=255)])
    arrival_time = marshmallow.fields.DateTime(allow_none=True,
                                               data_key='arrivaltime')

    class Meta:
        ordered = True
