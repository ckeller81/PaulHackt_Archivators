import type { ExhibitionModel } from "@/models/exhibition-model";
import { HttpClient } from "./http-client";

export class ImageService {
  httpClient: HttpClient;
  baseUrl: string;

  constructor() {
    this.baseUrl = `${import.meta.env.VITE_SERVICES_BASEURL}`;
    this.httpClient = new HttpClient("/api/images");
  }

  public async getExhibition() {
    return await this.httpClient.Get<ExhibitionModel>("exhibition");
  }

  public getImageUrl(imageId: string, width: number | null = null) {
    if (width) {
      return `${this.baseUrl}/images/${imageId}?width=${width}`;
    }

    return `${this.baseUrl}/images/${imageId}`;
  }
}
