from .models.facial_embedding_extractor import FacialVectorExtractor as VectorExtractor

import warnings
warnings.filterwarnings(
    action="ignore", 
    message="This overload of nonzero is deprecated:\n\tnonzero()", 
    category=UserWarning
)