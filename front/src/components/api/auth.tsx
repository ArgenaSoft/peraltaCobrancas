import axios from "axios";
import { env } from "process";



async function callGetCode(cpf: string, phone: string) {
    try {
      let response = await axios.get(env.API_URL + "/user/get_code/", {
        params: {
          cpf: cpf,
          phone: phone
        }
      });
      return response.data;
    }catch(error) {
      console.log(error);
      throw new Error("Error getting code");
    }
}

export { callGetCode };