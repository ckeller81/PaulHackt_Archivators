import type { SimilarImagesModel } from "@/models/similar-images-model";
import { HttpClient } from "./http-client";

export class SimilarImagesService {
  httpClient: HttpClient;
  baseUrl: string;

  constructor() {
    this.baseUrl = `${import.meta.env.VITE_SERVICES_BASEURL}`;
    this.httpClient = new HttpClient("/api/similarimages");
  }

  public async getSimilarImages(imageId: string) {
    return await this.httpClient.Get<SimilarImagesModel>(imageId);
  }
}
