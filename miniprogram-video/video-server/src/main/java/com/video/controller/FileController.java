package com.video.controller;

import com.video.common.Result;
import com.video.service.CosService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

/**
 * 文件上传控制器
 * 支持上传视频、封面图片到腾讯云 COS
 */
@Slf4j
@RestController
@RequestMapping("/api/file")
@RequiredArgsConstructor
public class FileController {

    private final CosService cosService;

    /**
     * 上传视频文件
     * POST /api/file/upload/video
     */
    @PostMapping("/upload/video")
    public Result<String> uploadVideo(
            @RequestParam("file") MultipartFile file,
            @RequestParam(required = false) Long videoId) {
        if (file.isEmpty()) {
            return Result.fail(400, "文件不能为空");
        }

        // 校验文件类型
        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("video/")) {
            return Result.fail(400, "请上传视频文件");
        }

        // 校验文件大小（最大 2GB）
        if (file.getSize() > 2L * 1024 * 1024 * 1024) {
            return Result.fail(400, "视频文件不能超过 2GB");
        }

        try {
            // 生成 COS 文件路径: videos/2024/01/{videoId}_{时间戳}.mp4
            String datePath = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy/MM"));
            String originalFilename = file.getOriginalFilename();
            String ext = "";
            if (StringUtils.hasText(originalFilename) && originalFilename.contains(".")) {
                ext = originalFilename.substring(originalFilename.lastIndexOf("."));
            } else {
                ext = ".mp4";
            }
            String timestamp = String.valueOf(System.currentTimeMillis());
            String key = String.format("videos/%s/%s_%s%s",
                    datePath,
                    videoId != null ? videoId : "upload",
                    timestamp,
                    ext);

            // 上传到 COS
            cosService.uploadFile(key, file, contentType);

            // 返回 COS 访问 URL
            String url = cosService.getFileUrl(key);
            log.info("视频上传成功: key={}, url={}", key, url);

            return Result.ok(url);
        } catch (Exception e) {
            log.error("视频上传失败", e);
            return Result.fail(500, "上传失败: " + e.getMessage());
        }
    }

    /**
     * 上传封面图片
     * POST /api/file/upload/cover
     */
    @PostMapping("/upload/cover")
    public Result<String> uploadCover(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return Result.fail(400, "文件不能为空");
        }

        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("image/")) {
            return Result.fail(400, "请上传图片文件");
        }

        if (file.getSize() > 10 * 1024 * 1024) {
            return Result.fail(400, "封面图片不能超过 10MB");
        }

        try {
            String datePath = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy/MM"));
            String originalFilename = file.getOriginalFilename();
            String ext = "";
            if (StringUtils.hasText(originalFilename) && originalFilename.contains(".")) {
                ext = originalFilename.substring(originalFilename.lastIndexOf("."));
            } else {
                ext = ".jpg";
            }
            String timestamp = String.valueOf(System.currentTimeMillis());
            String key = String.format("covers/%s/%s%s", datePath, timestamp, ext);

            cosService.uploadFile(key, file, contentType);
            String url = cosService.getFileUrl(key);

            return Result.ok(url);
        } catch (Exception e) {
            log.error("封面上传失败", e);
            return Result.fail(500, "上传失败: " + e.getMessage());
        }
    }

    /**
     * 上传通用文件
     * POST /api/file/upload
     */
    @PostMapping("/upload")
    public Result<String> upload(
            @RequestParam("file") MultipartFile file,
            @RequestParam(defaultValue = "files") String dir) {
        if (file.isEmpty()) {
            return Result.fail(400, "文件不能为空");
        }

        if (file.getSize() > 100 * 1024 * 1024) {
            return Result.fail(400, "文件不能超过 100MB");
        }

        try {
            String datePath = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy/MM"));
            String originalFilename = file.getOriginalFilename();
            String timestamp = String.valueOf(System.currentTimeMillis());
            String ext = "";
            if (StringUtils.hasText(originalFilename) && originalFilename.contains(".")) {
                ext = originalFilename.substring(originalFilename.lastIndexOf("."));
            }
            String key = String.format("%s/%s/%s%s", dir, datePath, timestamp, ext);

            cosService.uploadFile(key, file);
            String url = cosService.getFileUrl(key);

            return Result.ok(url);
        } catch (Exception e) {
            log.error("文件上传失败", e);
            return Result.fail(500, "上传失败: " + e.getMessage());
        }
    }
}
