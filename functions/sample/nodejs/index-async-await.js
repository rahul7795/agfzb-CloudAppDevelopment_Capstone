/**
 * Get all dealerships
 */

const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');

async function main(params) {
      const authenticator = new IamAuthenticator({ apikey: "mZBzXoWJcsH_RBkm61gW36PKvvHaqJLVbYXZ2lVpjBTU" })
      const cloudant = CloudantV1.newInstance({
          authenticator: authenticator
      });
      cloudant.setServiceUrl("https://b4fde291-319d-4463-9c6b-771132a03dec-bluemix.cloudantnosqldb.appdomain.cloud");
      try {
        let dbList = await cloudant.getAllDbs();
        return { "dbs": dbList.result };
      } catch (error) {
          return { error: error.description };
      }
}

