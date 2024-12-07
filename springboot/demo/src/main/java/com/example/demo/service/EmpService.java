package com.example.demo.service;

import com.example.demo.pojo.Emp;
import com.example.demo.pojo.PageBean;

import java.time.LocalDateTime;
import java.util.List;

public interface EmpService {
    PageBean page(Integer page, Integer pageSize, String name, Short gender, LocalDateTime begin, LocalDateTime end);

    void delete(List<Integer> ids);

    Emp login(Emp emp);
}
