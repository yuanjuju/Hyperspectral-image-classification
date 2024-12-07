package com.example.demo.mapper;

import com.example.demo.pojo.Dept;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface DeptMapper {
    @Select("select * from emp ")
    List<Dept> list();

    @Delete("delete from dept where id = #{id}")
    void deleteById(Integer id);

    @Insert("insert into dept(name, createTime, updateTime) values (#{name},#{createTime},#{updateTime})")
    void insert(Dept dept);
}
