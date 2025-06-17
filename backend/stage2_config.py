#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG第二阶段优化配置文件
提示词优化相关配置
"""

class Stage2OptimizationConfig:
    """第二阶段优化配置类"""
    
    # 提示词模板配置
    PROMPT_TEMPLATES = {
        "general": {
            "version": "v2.0",
            "role_definition": "你是一个智能助手",
            "core_principles": [
                "你只能基于【背景资料】中的信息回答问题",
                "禁止使用你的预训练知识或常识来补充回答",
                "如果背景资料不足，必须明确说明"
            ],
            "response_rules": {
                "has_info": "请基于这些信息详细回答，并标注具体来源文档",
                "incomplete_info": "请基于现有信息部分回答，并说明哪些方面的信息不足",
                "no_info": "根据提供的背景资料，无法找到相关信息来回答这个问题"
            }
        },
        
        "targeted": {
            "version": "v2.0",
            "role_definition": "你是一个专业的文档分析智能助手",
            "core_principles": [
                "你只能基于【背景资料】中的信息回答问题",
                "重点关注来自目标文档的内容",
                "禁止使用预训练知识或推测来补充回答",
                "必须明确标注信息来源"
            ],
            "response_rules": {
                "has_target_info": "详细分析并回答，明确引用文档名称和具体内容",
                "incomplete_target_info": "基于现有信息回答，并说明哪些信息缺失",
                "no_target_info": "在提供的背景资料中，未找到关于[目标文档]的相关信息"
            }
        }
    }
    
    # 上下文质量优化配置
    CONTEXT_ENHANCEMENT = {
        "enable_relevance_scoring": True,  # 启用相关性评分
        "relevance_weight": 0.3,           # 相关性权重
        "max_context_length": 2000,        # 最大上下文长度
        "context_format": {
            "include_source": True,         # 包含来源信息
            "include_score": True,          # 包含相关性评分
            "separator": "---"              # 内容分隔符
        }
    }
    
    # 知识边界控制配置
    KNOWLEDGE_BOUNDARY = {
        "strict_mode": True,                # 严格模式
        "fallback_responses": {
            "no_knowledge": "对不起，我在当前知识库中没有找到与您问题相关的信息。",
            "insufficient_info": "根据提供的背景资料，信息不足以完整回答您的问题。",
            "out_of_scope": "您的问题超出了当前知识库的范围。"
        },
        "boundary_keywords": [
            "众所周知", "一般来说", "通常", "据我所知", 
            "根据常识", "普遍认为", "大家都知道"
        ]
    }
    
    # 响应质量评估配置
    QUALITY_ASSESSMENT = {
        "enable_assessment": True,
        "quality_indicators": {
            "source_attribution": ["文档", "来源", "根据", "基于"],
            "knowledge_boundary": ["没有找到", "信息不足", "无法", "不能"],
            "evidence_based": ["背景资料", "提供的信息", "文档中"],
            "hallucination_words": ["众所周知", "一般来说", "通常", "据我所知"]
        }
    }
    
    # API响应增强配置
    API_ENHANCEMENT = {
        "include_optimization_stage": True,  # 包含优化阶段标识
        "include_source_files": True,        # 包含源文件信息
        "include_quality_score": True,       # 包含质量评分
        "response_metadata": {
            "optimization_stage": "stage2_prompt_optimization",
            "prompt_version": "v2.0",
            "features": [
                "role_definition",
                "context_enhancement", 
                "knowledge_boundary",
                "source_attribution"
            ]
        }
    }

class PromptBuilder:
    """提示词构建器"""
    
    @staticmethod
    def build_system_prompt(prompt_type, context, user_question, **kwargs):
        """构建系统提示词"""
        config = Stage2OptimizationConfig.PROMPT_TEMPLATES.get(prompt_type, {})
        
        if prompt_type == "general":
            return PromptBuilder._build_general_prompt(config, context, user_question)
        elif prompt_type == "targeted":
            target_files = kwargs.get('target_files', [])
            return PromptBuilder._build_targeted_prompt(config, context, user_question, target_files)
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
    
    @staticmethod
    def _build_general_prompt(config, context, user_question):
        """构建通用提示词"""
        role = config.get("role_definition", "")
        principles = config.get("core_principles", [])
        
        principles_text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(principles)])
        
        prompt = f"""{role}。请根据下面提供的【背景资料】来回答用户提出的【问题】。

**核心原则：**
{principles_text}

**回答规范：**
- 如果【背景资料】中有相关信息：{config.get("response_rules", {}).get("has_info", "")}
- 如果【背景资料】中信息不完整：{config.get("response_rules", {}).get("incomplete_info", "")}
- 如果【背景资料】中完全没有相关信息：{config.get("response_rules", {}).get("no_info", "")}

【背景资料】:
{context}

【问题】:
{user_question}

【你的回答】:
请严格基于上述背景资料回答问题："""
        
        return prompt
    
    @staticmethod
    def _build_targeted_prompt(config, context, user_question, target_files):
        """构建针对特定文档的提示词"""
        role = config.get("role_definition", "")
        principles = config.get("core_principles", [])
        target_files_str = '、'.join(target_files) if target_files else "特定文档"
        
        principles_text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(principles)])
        
        prompt = f"""{role}。你的任务是基于提供的【背景资料】分析并回答用户针对特定文档的【问题】。

**目标文档：** {target_files_str}

**核心原则：**
{principles_text}

**回答规范：**
- 如果背景资料中有目标文档的相关信息：{config.get("response_rules", {}).get("has_target_info", "")}
- 如果背景资料中目标文档信息不完整：{config.get("response_rules", {}).get("incomplete_target_info", "")}
- 如果背景资料中没有目标文档的相关信息：{config.get("response_rules", {}).get("no_target_info", "")}

【背景资料】:
{context}

【问题】:
{user_question}

【你的回答】:
请基于上述背景资料分析目标文档并回答问题："""
        
        return prompt

class QualityAssessor:
    """回答质量评估器"""
    
    @staticmethod
    def assess_response_quality(response):
        """评估回答质量"""
        config = Stage2OptimizationConfig.QUALITY_ASSESSMENT
        
        if not config.get("enable_assessment", False):
            return {"quality_score": 1.0, "indicators": {}}
        
        indicators = config.get("quality_indicators", {})
        
        # 评估各项指标
        results = {}
        total_score = 0
        
        # 来源标注
        source_words = indicators.get("source_attribution", [])
        has_source = any(word in response for word in source_words)
        results["source_attribution"] = has_source
        total_score += 1 if has_source else 0
        
        # 知识边界
        boundary_words = indicators.get("knowledge_boundary", [])
        has_boundary = any(word in response for word in boundary_words)
        results["knowledge_boundary"] = has_boundary
        
        # 基于证据
        evidence_words = indicators.get("evidence_based", [])
        has_evidence = any(word in response for word in evidence_words)
        results["evidence_based"] = has_evidence
        total_score += 1 if has_evidence else 0
        
        # 避免幻觉
        hallucination_words = indicators.get("hallucination_words", [])
        has_hallucination = any(word in response for word in hallucination_words)
        results["avoid_hallucination"] = not has_hallucination
        total_score += 1 if not has_hallucination else 0
        
        # 计算综合质量分数
        max_score = 3  # source_attribution + evidence_based + avoid_hallucination
        quality_score = total_score / max_score if max_score > 0 else 0
        
        return {
            "quality_score": quality_score,
            "indicators": results,
            "assessment_enabled": True
        }

# 导出配置实例
stage2_config = Stage2OptimizationConfig()
prompt_builder = PromptBuilder()
quality_assessor = QualityAssessor()
