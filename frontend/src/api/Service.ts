export default class APIService {
  static async GetData(url: string): Promise<any> {
    try {
      const response: Response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          Accept: "application/json",
        },
        
      });
      
      return await response.json();
    } catch (error) {
      console.error(error);
      throw error;
    }
  }

  static async PostData(url: string, body: any): Promise<any> {
    try {
      const response: Response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          Accept: "application/json",
        },
        body: JSON.stringify(body),
      });

      return await response.json();
    } catch (error) {
      console.error(error);
      throw error;
    }
  }
}
