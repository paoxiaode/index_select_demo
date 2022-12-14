import torch
from torch import nn
import os
from pattern_match import pattern_matching
ops_library_abs_path = os.path.abspath("/workspace2/index_mul_demo/source/build/liboc20_customized_ops.so")
torch.ops.load_library(ops_library_abs_path)


class InteractionPPBlock(torch.jit.ScriptModule):
    def __init__(
        self,
       in_dim,
       out_dim,
       num_elements
    ):
        super(InteractionPPBlock, self).__init__()
        self.lin_sbf = nn.Linear(128, 64)
        self.lin_down = nn.Linear(in_dim, out_dim)
        self.act = nn.ReLU()

    @torch.jit.script_method
    def forward(self, x_kj, idx_kj, sbf):
        # x_kj = self.act(self.lin_down(x_kj))
        # # Transform via 2D spherical basis.
        # sbf = self.lin_sbf(sbf)
        # sbf = sbf.relu()
        # sbf = sbf - 1
        # sbf = sbf*sbf
        x_kj = torch.index_select(x_kj, 0, idx_kj) * sbf 

        # lerp demo
        # x_kj = torch.lerp(x_kj, sbf, 0.5)
        return x_kj


def main():
    in_dim = 128
    out_dim = 64
    num_elements = 355984
    x = torch.rand((num_elements, in_dim)).to("cuda:0")
    y = torch.randperm(num_elements).to("cuda:0")

    z = torch.rand((num_elements, in_dim)).to("cuda:0")
    model = InteractionPPBlock(in_dim, out_dim, num_elements).to("cuda:0")
    # pattern_matching(model.graph)
    with torch.jit.fuser("fuser2"):
        for i in range(2):
            print(i)
            res = model(x, y, z)
    # loss = torch.mean(res)
    # loss.backward()
    print(model.graph)
    print("finish backward")
    return 0





if __name__ == "__main__":
    main()