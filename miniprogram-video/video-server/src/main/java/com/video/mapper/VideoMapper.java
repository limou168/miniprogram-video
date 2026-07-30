package com.video.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.video.entity.Video;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface VideoMapper extends BaseMapper<Video> {

    /**
     * 全文搜索（MATCH AGAINST + ngram 中文分词）
     * 支持多字段：title, director, actors, tags, description
     */
    Page<Video> searchFulltext(Page<Video> page, @Param("keyword") String keyword);

    /**
     * 全文搜索计数
     */
    Long countFulltext(@Param("keyword") String keyword);

    /**
     * 搜索建议（仅查标题，用于前端自动补全）
     */
    List<String> searchSuggestions(@Param("keyword") String keyword, @Param("limit") Integer limit);

    /**
     * LIKE 模糊搜索回退（全文搜索无结果时使用）
     */
    Page<Video> searchLike(Page<Video> page, @Param("keyword") String keyword);

    /**
     * LIKE 模糊搜索计数
     */
    Long countLike(@Param("keyword") String keyword);
}
