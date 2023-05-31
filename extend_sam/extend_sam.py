# copyright ziqi-jin
import torch
import torch.nn as nn
from segment_anything import sam_model_registry
from .image_encoder_adapter import BaseImgEncodeAdapter
from .mask_decoder_adapter import BaseMaskDecoderAdapter, SemMaskDecoderAdapter
from .prompt_encoder_adapter import BasePromptEncodeAdapter


class BaseExtendSam(nn.Module):

    def __init__(self, ckpt_path=None, fix_img_en=False, fix_promt_en=False, fix_mask_de=False):
        super(BaseExtendSam, self).__init__()
        self.ori_sam = sam_model_registry['default'](ckpt_path)
        self.img_adapter = BaseImgEncodeAdapter(self.ori_sam, fix=fix_img_en)
        self.prompt_adapter = BasePromptEncodeAdapter(self.ori_sam, fix=fix_promt_en)
        self.mask_adapter = BaseMaskDecoderAdapter(self.ori_sam, fix=fix_mask_de)

    def forward(self, img):
        x = self.img_adapter(img)
        points = None
        boxes = None
        masks = None

        sparse_embeddings, dense_embeddings = self.prompt_adapter(
            points=points,
            boxes=boxes,
            masks=masks,
        )
        multimask_output = True
        low_res_masks, iou_predictions = self.mask_adapter(
            image_embeddings=x,
            image_pe=self.prompt_encoder.get_dense_pe(),
            sparse_prompt_embeddings=sparse_embeddings,
            dense_prompt_embeddings=dense_embeddings,
            multimask_output=multimask_output,
        )
        return low_res_masks, iou_predictions


class SemanticSam(BaseExtendSam):

    def __init__(self, ckpt_path=None, fix_img_en=False, fix_promt_en=False, fix_mask_de=False):
        super().__init__(ckpt_path=ckpt_path, fix_img_en=fix_promt_en, fix_promt_en=False, fix_mask_de=fix_mask_de)
        self.mask_adapter = SemMaskDecoderAdapter(self.ori_sam, fix=fix_img_en)

