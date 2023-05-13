import type { ApiResultModel } from "./api-result-model";

export interface SimilarImagesModel extends ApiResultModel {
  images: SimilarImageModel[];
}

export interface SimilarImageModel {
  image_id: string;
  score: number;
}
