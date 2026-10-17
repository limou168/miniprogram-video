package com.video.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.video.dto.CategoryVO;
import com.video.entity.Category;

import java.util.List;

public interface CategoryService extends IService<Category> {

    /**
     * 获取全部分类列表
     */
    List<CategoryVO> listAll();
}
