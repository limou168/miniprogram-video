package com.video.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.video.dto.PageResult;
import com.video.dto.VideoCardVO;
import com.video.dto.VideoVO;
import com.video.entity.Video;

import java.util.List;

public interface VideoService extends IService<Video> {

    /**
     * 分页获取影视列表（可按分类、年份筛选、排序）
     */
    PageResult<VideoCardVO> getVideoList(Integer page, Integer size, Long categoryId,
                                          String keyword, Integer year, String orderBy);

    /**
     * 获取影视详情
     */
    VideoVO getVideoDetail(Long id);

    /**
     * 获取热门推荐
     */
    PageResult<VideoCardVO> getHotVideos();

    /**
     * 搜索影视（使用 MySQL FULLTEXT 索引 + ngram 中文分词）
     * 搜索字段：标题、导演、演员、标签、简介
     */
    PageResult<VideoCardVO> search(String keyword, Integer page, Integer size);

    /**
     * 搜索建议（用于前端输入时自动补全/下拉提示）
     * 仅根据标题匹配，返回匹配的标题列表
     */
    List<String> searchSuggestions(String keyword, Integer limit);
}
