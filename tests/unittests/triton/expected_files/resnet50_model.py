import towhee
import numpy
from towhee import ops
import triton_python_backend_utils as pb_utils


class TritonPythonModel:

    def initialize(self, args):

        device = "cpu"
        if args["model_instance_kind"] == "GPU":
            device = int(args["model_instance_device_id"])        
        # create op instance
        task = getattr(ops, 'image_embedding')
        init_args = {"model_name": "resnet50"}
        self.op = getattr(task, 'timm')(**init_args)
        self.op._device = device
        if hasattr(self.op, "to_device"):
            self.op.to_device()

    def execute(self, requests):

        responses = []

        for request in requests:
            # get input tensors from request
            in0 = pb_utils.get_input_tensor_by_name(request, 'INPUT0')
            in1 = pb_utils.get_input_tensor_by_name(request, 'INPUT1')

            # create input args from tensors
            arg0 = towhee._types.Image(in0.as_numpy(), in1.as_numpy()[0].decode('utf-8'))

            # call callable object
            result0 = self.op(arg0)

            # convert results to tensors
            out0 = pb_utils.Tensor('OUTPUT0', numpy.array(result0, numpy.float32))

            # organize response
            response = pb_utils.InferenceResponse(output_tensors=[out0])
            responses.append(response)

        return responses

    def finalize(self):
        pass
