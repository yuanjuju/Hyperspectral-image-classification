package com.example.demo.controller;

import com.example.demo.utils.AliOSSUtils;
import jakarta.servlet.ServletOutputStream;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import java.net.URLEncoder;
import java.io.IOException;


import java.io.InputStream;

@RestController
@RequestMapping("/api")
public class DownloadController {
    @Autowired
    private AliOSSUtils aliOSSUtils;




    @GetMapping("/download")
    public void downloadFile(@RequestParam("fileName") String fileName, HttpServletResponse response) {
        InputStream inputStream = null;
        ServletOutputStream outputStream = null;

        try {
            // 下载文件流并重试3次
            inputStream = retryDownload(fileName);
            if (inputStream == null) {
                response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
                return;
            }

            // 对文件名进行 URL 编码，避免特殊字符问题
            String encodedFileName = URLEncoder.encode(fileName, "UTF-8").replaceAll("\\+", "%20");

            // 设置 HTTP 响应头，支持文件下载
            response.setContentType("application/octet-stream");
            response.setHeader("Content-Disposition", "attachment; filename=\"" + encodedFileName + "\"");

            // 设置 Content-Length 响应头，确保文件大小正确
            response.setHeader("Content-Length", String.valueOf(inputStream.available()));

            // 获取响应的输出流
            outputStream = response.getOutputStream();

            // 使用较大的缓冲区来提高性能
            byte[] buffer = new byte[8192]; // 8 KB 缓冲区
            int bytesRead;

            // 将文件内容写入响应输出流
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }

            outputStream.flush();
        } catch (org.apache.catalina.connector.ClientAbortException e) {
            // 客户端中断下载请求，不做处理，直接返回
            System.out.println("客户端中断下载连接: " + e.getMessage());
        } catch (Exception e) {
            e.printStackTrace();
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
        } finally {
            // 关闭输入输出流
            try {
                if (inputStream != null) {
                    inputStream.close();
                }
                if (outputStream != null) {
                    outputStream.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    // 重试下载逻辑，最多重试3次
    private InputStream retryDownload(String fileName) {
        int retryCount = 3;
        InputStream inputStream = null;
        while (retryCount > 0) {
            try {
                inputStream = aliOSSUtils.download(fileName);
                if (inputStream != null) {
                    return inputStream; // 下载成功，返回文件流
                }
            } catch (Exception e) {
                retryCount--;
                e.printStackTrace();
                if (retryCount > 0) {
                    System.out.println("下载失败，重试 " + retryCount + " 次...");
                    try {
                        Thread.sleep(1000); // 延迟1秒后再试
                    } catch (InterruptedException ie) {
                        ie.printStackTrace();
                    }
                } else {
                    System.out.println("下载失败，已达到最大重试次数。");
                }
            }
        }
        return null; // 重试次数用尽仍然失败
    }



}
