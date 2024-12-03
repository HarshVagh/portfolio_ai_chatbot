import { PutObjectCommand } from "@aws-sdk/client-s3";
import { s3Client } from "./awsClients.js";

export const deployToS3 = async (content, bucketName, s3Key) => {
  try {
    const command = new PutObjectCommand({
      Bucket: bucketName,
      Key: s3Key,
      Body: Buffer.from(content, "utf-8"),
      ContentType: "text/html",
    });
    await s3Client.send(command);
    return `https://${bucketName}.s3.amazonaws.com/${s3Key}`;
  } catch (error) {
    console.error(`Error deploying to S3 at ${bucketName}/${s3Key}:`, error);
    return "";
  }
};
