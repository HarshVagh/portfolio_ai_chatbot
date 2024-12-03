import { GetObjectCommand } from "@aws-sdk/client-s3";
import { s3Client } from "./awsClients.js";

export const getTextFromS3 = async (bucketName, keyName) => {
  try {
    const command = new GetObjectCommand({ Bucket: bucketName, Key: keyName });
    const response = await s3Client.send(command);
    const stream = response.Body;
    const chunks = [];
    
    for await (const chunk of stream) {
      chunks.push(chunk);
    }
    
    const buffer = Buffer.concat(chunks);
    return buffer.toString("utf-8");
  } catch (error) {
    console.error(`Error fetching S3 object from ${bucketName}/${keyName}:`, error);
    return "";
  }
};
