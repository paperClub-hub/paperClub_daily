#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2023-04-19 10:44
# @Author   : NING MEI
# @Desc     :


from typing import Union


def hash_based_dedup(embeddings: Union[torch.Tensor, np.ndarray]):
	""" 二维向量组去重：基于hash编码值进行去重 """
	seen_hashes = set()
	to_remove = []
	for i, embedding in enumerate(embeddings):
		# print(f"dtype: {embedding.dtype}, type: {type(emb)}")
		if isinstance(embedding, torch.Tensor):
			embedding = embedding.detach().cpu().numpy()

		# embedding = np.float16(embedding)
		h = hash(np.round(embedding, 2).tobytes())
		if h in seen_hashes:
			to_remove.append(i)
			continue
		seen_hashes.add(h)

	return to_remove




