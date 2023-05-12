import superagent from "superagent";
import type { ApiResultModel } from "../models/api-result-model";

export class HttpClient {
  private baseApiUrl: string;

  constructor(apiUrl: string) {
    this.baseApiUrl = `${import.meta.env.VITE_SERVICES_BASEURL}${apiUrl}`;
  }

  async Post<Result extends ApiResultModel, Data>(endpoint: string, data: Data): Promise<Result> {
    const url = this.getUrl(endpoint);
    try {
      const response = await superagent
        .post(url)
        .type("application/json")
        .send(JSON.stringify(data));
      return response.body as Result;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async Get<Result extends ApiResultModel>(endpoint: string = ""): Promise<Result> {
    const url = this.getUrl(endpoint);
    try {
      const response = await superagent.get(url);
      return response.body as Result;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async Put<Result extends ApiResultModel, Data>(endpoint: string, data: Data): Promise<Result> {
    const url = this.getUrl(endpoint);
    try {
      const response = await superagent
        .put(url)
        .type("application/json")
        .send(JSON.stringify(data));
      return response.body as Result;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async Patch<Result extends ApiResultModel, Data>(endpoint: string, data: Data): Promise<Result> {
    const url = this.getUrl(endpoint);
    try {
      const response = await superagent
        .patch(url)
        .type("application/json")
        .send(JSON.stringify(data));
      return response.body as Result;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async Delete<Result extends ApiResultModel>(endpoint: string): Promise<Result> {
    const url = this.getUrl(endpoint);
    try {
      const response = await superagent.delete(url);
      return response.body as Result;
    } catch (error) {
      return this.handleError(error);
    }
  }

  private async handleError<Result extends ApiResultModel>(error: any) {
    if (error.response && error.response.status >= 400) {
      return error.response.body as Result;
    }

    throw error;
  }

  private getUrl(endpoint: string) {
    return `${this.baseApiUrl}/${endpoint}`;
  }
}
