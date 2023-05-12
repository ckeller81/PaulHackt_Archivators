import type { ApiResultModel } from "./api-result-model";

export interface ImageDescriptionModel extends ApiResultModel {
  description: string;
  title: string;
  year: string;
}
