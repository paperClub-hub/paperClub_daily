# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import intent_pb2 as intent__pb2


class IntentServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Result = channel.unary_unary(
                '/intent.IntentService/Result',
                request_serializer=intent__pb2.IntentRequest.SerializeToString,
                response_deserializer=intent__pb2.IntentResponse.FromString,
                )


class IntentServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Result(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_IntentServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Result': grpc.unary_unary_rpc_method_handler(
                    servicer.Result,
                    request_deserializer=intent__pb2.IntentRequest.FromString,
                    response_serializer=intent__pb2.IntentResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'intent.IntentService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class IntentService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Result(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/intent.IntentService/Result',
            intent__pb2.IntentRequest.SerializeToString,
            intent__pb2.IntentResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
