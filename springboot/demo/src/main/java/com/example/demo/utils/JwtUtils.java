package com.example.demo.utils;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import java.util.Date;
import java.util.Map;

public class JwtUtils {

    // 统一使用一个 SecretKey 实例
    private static final SecretKey SECRET_KEY = generateSecretKey();
    private static final Long EXPIRE = 43200000L; // 12小时

    // 生成 JWT
    public static String generateJwt(Map<String, Object> claims) {
        return Jwts.builder()
                .addClaims(claims)
                .signWith(SignatureAlgorithm.HS256, SECRET_KEY)
                .setExpiration(new Date(System.currentTimeMillis() + EXPIRE))
                .compact();
    }

    // 解析 JWT
    public static Claims parseJwt(String jwt) {
        return Jwts.parser()
                .setSigningKey(SECRET_KEY)
                .parseClaimsJws(jwt)
                .getBody();
    }

    // 生成 HMAC SHA256 密钥
    private static SecretKey generateSecretKey() {
        try {
            KeyGenerator keyGen = KeyGenerator.getInstance("HmacSHA256");
            keyGen.init(256); // 256 位密钥
            return keyGen.generateKey();
        } catch (Exception e) {
            throw new RuntimeException("生成密钥时出错", e);
        }
    }
}
