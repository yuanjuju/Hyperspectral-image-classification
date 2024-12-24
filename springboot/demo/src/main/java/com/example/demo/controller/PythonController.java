package com.example.demo.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.client.RestTemplate;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@RestController
@RequestMapping("/api")
public class PythonController {

    @Autowired
    private RestTemplate restTemplate;

    @PostMapping("/uploadfile")
    public ResponseEntity<byte[]> handleFileUpload(@RequestParam("file") MultipartFile file) {
        System.out.println("File received, forwarding to Flask server...");

        // Flask 服务的 URL
        String flaskUrl = "http://localhost:5000/api/upload"; // 替换为实际的 Flask 服务地址

        // 准备转发请求的表单数据
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", file.getResource());

        // 创建请求头
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        // 创建HttpEntity
        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        try {
            // 转发请求到 Flask 后端
            ResponseEntity<String> response = restTemplate.exchange(flaskUrl, HttpMethod.POST, requestEntity, String.class);

            // 获取 Flask 返回的响应体 (假设它是一个包含 predictions 字段的 JSON)
            String flaskResponse = response.getBody();

            // 使用 Jackson 解析 Flask 返回的 JSON 字符串
            JsonNode jsonNode = new ObjectMapper().readTree(flaskResponse);

            // 如果 Flask 返回了 predictions 字段
            if (jsonNode.has("predictions")) {
                // 将 JSON 数据转换为字节数组
                byte[] fileContent = flaskResponse.getBytes();

                // 设置响应头，指示这是一个文件下载
                HttpHeaders responseHeaders = new HttpHeaders();
                responseHeaders.add("Content-Disposition", "attachment; filename=predictions.json");
                responseHeaders.add("Content-Type", "application/json");

                return new ResponseEntity<>(fileContent, responseHeaders, HttpStatus.OK);
            } else {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("No predictions found".getBytes());
            }

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(("Error: " + e.getMessage()).getBytes());
        }
    }
}
