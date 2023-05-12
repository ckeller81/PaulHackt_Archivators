import type { ImageDescriptionModel } from "@/models/image-description-model";
import { HttpClient } from "./http-client";

export class DescriptionService {
  httpClient: HttpClient;

  constructor() {
    this.httpClient = new HttpClient("/api/description");
  }

  public async get(imageId: string) {
    return await this.httpClient.Get<ImageDescriptionModel>(imageId);
  }
}
