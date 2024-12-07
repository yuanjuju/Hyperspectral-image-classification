package com.example.demo.utils;
import com.aliyun.oss.ClientException;
import com.aliyun.oss.OSS;
import com.aliyun.oss.OSSClientBuilder;
import com.aliyun.oss.OSSException;
import com.aliyun.oss.common.auth.CredentialsProviderFactory;
import com.aliyun.oss.common.auth.EnvironmentVariableCredentialsProvider;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.UUID;

@Component
public class AliOSSUtils {
    private String endpoint = "https://oss-cn-hangzhou.aliyuncs.com";
    private String accessKeyId = "LTAI5tFi7B3o1DhxBqGq1QDj";
    private String accseeKeySecret = "eUHvEYoz7sjck1d2eSrKkpSi9xWoiJ";
    private String bucketName = "ycgweb";
    public String upload(MultipartFile file) throws Exception  {
        //获取上传的文件的输入流
        InputStream inputStream = file.getInputStream();
        //避免文件覆盖
        String originalFilename = file.getOriginalFilename();
        String fileName = UUID.randomUUID().toString() + originalFilename.substring(originalFilename.lastIndexOf("."));
        OSS ossClient = new OSSClientBuilder().build(endpoint, accessKeyId, accseeKeySecret);
        ossClient.putObject(bucketName, fileName, inputStream);

        String url = "https://" + bucketName + "." + endpoint.replace("https://", "") + "/" + fileName;
        ossClient.shutdown();
        return url;
    }
    public InputStream download(String fileName) throws Exception {
        OSS ossClient = new OSSClientBuilder().build(endpoint, accessKeyId, accseeKeySecret);
        try {
            return ossClient.getObject(bucketName, fileName).getObjectContent();
        } catch (OSSException e) {
            e.printStackTrace();
            throw new Exception("文件下载失败：" + e.getMessage());
        } finally {
            ossClient.shutdown();
        }
    }



}

