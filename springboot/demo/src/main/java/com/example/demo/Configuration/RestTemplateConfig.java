//package com.example.demo.Configuration;
//
//import org.apache.hc.client5.http.impl.classic.HttpClients;
//import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
//import org.apache.hc.client5.http.impl.io.PoolingHttpClientConnectionManager;
//import org.apache.hc.core5.ssl.SSLContextBuilder;
//import org.apache.hc.client5.http.config.RequestConfig;
//import org.springframework.context.annotation.Bean;
//import org.springframework.context.annotation.Configuration;
//import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
//import org.springframework.web.client.RestTemplate;
//
//@Configuration
//public class RestTemplateConfig {
//
//    @Bean
//    public RestTemplate restTemplate() {
//        // 设置连接超时和读取超时
//        int connectionTimeout = 300000;  // 300秒连接超时
//        int readTimeout = 300000;       // 300秒读取超时
//
//        // 配置请求设置
//        RequestConfig requestConfig = RequestConfig.custom()
//                .setConnectTimeout(connectionTimeout)
//                .setResponseTimeout(readTimeout)
//                .build();
//
//        // 使用 HttpClient 5.x 构建 HttpClient
//        PoolingHttpClientConnectionManager connectionManager = new PoolingHttpClientConnectionManager();
//        connectionManager.setDefaultMaxPerRoute(20);
//        connectionManager.setMaxTotal(200);
//
//        // 使用 HttpClientBuilder 配置 HttpClient
//        CloseableHttpClient httpClient = HttpClients.custom()
//                .setDefaultRequestConfig(requestConfig)
//                .setConnectionManager(connectionManager)
//                .build();
//
//        // 返回 RestTemplate，确保它使用配置的 HttpClient
//        return new RestTemplate(new HttpComponentsClientHttpRequestFactory(httpClient));
//    }
//}
