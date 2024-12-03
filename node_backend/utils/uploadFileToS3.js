import { PutObjectCommand } from "@aws-sdk/client-s3";
import { s3Client } from "./awsClients.js";

export const uploadFileToS3 = async (textContent, userId, filename, bucketName) => {
  try {
    const s3FilePath = `resumes/${userId}/${filename}`;
    const command = new PutObjectCommand({
      Bucket: bucketName,
      Key: s3FilePath,
      Body: Buffer.from(textContent, "utf-8"),
      ContentType: "text/plain",
    });
    await s3Client.send(command);
    return `https://${bucketName}.s3.amazonaws.com/${s3FilePath}`;
  } catch (error) {
    console.error(`Error uploading file to S3 at ${bucketName}/${s3FilePath}:`, error);
    return "";
  }
};
