package com.video.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.video.dto.VideoSourceVO;
import com.video.entity.VideoSource;
import com.video.mapper.VideoSourceMapper;
import com.video.service.VideoSourceService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class VideoSourceServiceImpl extends ServiceImpl<VideoSourceMapper, VideoSource> implements VideoSourceService {

    @Override
    public List<VideoSourceVO> getSources(Long videoId, Integer episodeNumber) {
        return list(new LambdaQueryWrapper<VideoSource>()
                .eq(VideoSource::getVideoId, videoId)
                .eq(VideoSource::getEpisodeNumber, episodeNumber != null ? episodeNumber : 0)
                .eq(VideoSource::getStatus, 1)
                .orderByAsc(VideoSource::getSortOrder))
                .stream()
                .map(s -> VideoSourceVO.builder()
                        .id(s.getId())
                        .sourceName(s.getSourceName())
                        .sourceUrl(s.getSourceUrl())
                        .episodeNumber(s.getEpisodeNumber())
                        .build())
                .collect(Collectors.toList());
    }
}
