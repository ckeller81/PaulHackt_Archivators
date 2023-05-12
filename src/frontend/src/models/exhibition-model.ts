import type { ApiResultModel } from "./api-result-model";

export interface ExhibitionModel extends ApiResultModel {
  title: string;
  imageIds: string[];
}
