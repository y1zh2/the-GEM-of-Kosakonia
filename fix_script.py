#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
根据指定修改更新模型中的反应，并运行memote生成报告
"""

import cobra
import subprocess
import os
import sys

def update_cmcbtfl_reaction(model):
    """
    根据要求修改CMCBTFL反应: cmcbtt_c + fe3_e --> fe3cmcbtt_c
    """
    print("修改CMCBTFL反应...")
    
    try:
        # 获取CMCBTFL反应
        reaction = model.reactions.get_by_id('CMCBTFL')
        
        # 记录原始反应
        original_reaction = reaction.build_reaction_string()
        print(f"原始反应: {original_reaction}")
        
        # 清除所有代谢物
        reaction.subtract_metabolites(reaction.metabolites)
        
        # 添加反应物: cmcbtt_c + fe3_e
        cmcbtt_c = model.metabolites.get_by_id('cmcbtt_c')
        fe3_e = model.metabolites.get_by_id('fe3_e')
        
        # 检查fe3cmcbtt_c是否存在，如果不存在则创建
        fe3cmcbtt_id = 'fe3cmcbtt_c'
        if fe3cmcbtt_id not in model.metabolites:
            print(f"创建新的代谢物: {fe3cmcbtt_id}")
            # 复制cmcbtt_c的属性并添加铁
            new_metabolite = cobra.Metabolite(
                fe3cmcbtt_id,
                name="铁(III)羧霉菌素B",
                formula="C33H48FeN5O13",  # 添加Fe到原始cmcbtt_c的公式
                charge=3,  # 假设电荷为3，与fe3_e一致
                compartment='c'
            )
            model.add_metabolites([new_metabolite])
            fe3cmcbtt_c = new_metabolite
        else:
            fe3cmcbtt_c = model.metabolites.get_by_id(fe3cmcbtt_id)
        
        # 重设为新的反应: cmcbtt_c + fe3_e --> fe3cmcbtt_c
        reaction.add_metabolites({
            cmcbtt_c: -1,
            fe3_e: -1,
            fe3cmcbtt_c: 1
        })
        
        print(f"更新后的反应: {reaction.build_reaction_string()}")
        return True
    except Exception as e:
        print(f"修改CMCBTFL反应时出错: {str(e)}")
        return False

def update_salchs4feabcpp_reaction(model):
    """
    根据要求修改SALCHS4FEabcpp反应: atp_c + h2o_c + salchs4fe_p --> adp_c + pi_c + salchs4fe_c
    """
    print("修改SALCHS4FEabcpp反应...")
    
    try:
        # 获取SALCHS4FEabcpp反应
        reaction = model.reactions.get_by_id('SALCHS4FEabcpp')
        
        # 记录原始反应
        original_reaction = reaction.build_reaction_string()
        print(f"原始反应: {original_reaction}")
        
        # 清除所有代谢物
        reaction.subtract_metabolites(reaction.metabolites)
        
        # 获取需要的代谢物
        atp_c = model.metabolites.get_by_id('atp_c')
        h2o_c = model.metabolites.get_by_id('h2o_c')
        salchs4fe_p = model.metabolites.get_by_id('salchs4fe_p')
        adp_c = model.metabolites.get_by_id('adp_c')
        pi_c = model.metabolites.get_by_id('pi_c')
        salchs4fe_c = model.metabolites.get_by_id('salchs4fe_c')
        
        # 重设为新的反应: atp_c + h2o_c + salchs4fe_p --> adp_c + pi_c + salchs4fe_c
        reaction.add_metabolites({
            atp_c: -1,
            h2o_c: -1,
            salchs4fe_p: -1,
            adp_c: 1,
            pi_c: 1,
            salchs4fe_c: 1
        })
        
        print(f"更新后的反应: {reaction.build_reaction_string()}")
        return True
    except Exception as e:
        print(f"修改SALCHS4FEabcpp反应时出错: {str(e)}")
        return False

def add_agpatr_bs_reaction(model):
    """
    添加AGPATr_BS反应: 10 pmtcoa_c + 3 tdcoa_c + 1 1ag3p_BS_c + 7 fa11coa_c + 17 fa12coa_c + 1 fa1coa_c + 20 fa3coa_c + 34 fa4coa_c + 5 fa6coa_c + 3 strcoa_c ⇌ coa_c + 1 12dag3p_BS_c
    """
    print("添加AGPATr_BS反应...")
    
    try:
        # 检查反应是否已存在
        if 'AGPATr_BS' in model.reactions:
            reaction = model.reactions.get_by_id('AGPATr_BS')
            print(f"反应AGPATr_BS已存在，将更新: {reaction.build_reaction_string()}")
            # 清除所有代谢物
            reaction.subtract_metabolites(reaction.metabolites)
        else:
            # 创建新反应
            reaction = cobra.Reaction('AGPATr_BS')
            reaction.name = "1-acylglycerol-3-phosphate O-acyltransferase (BS specific)"
            reaction.subsystem = "Lipid Metabolism"
            model.add_reactions([reaction])
            print("创建新反应AGPATr_BS")
        
        # 确保所有代谢物存在
        metabolites = {
            'pmtcoa_c': '棕榈酸辅酶A',
            'tdcoa_c': '十四烷酸辅酶A',
            '1ag3p_BS_c': '1-酰基甘油-3-磷酸(BS特异性)',
            'fa11coa_c': '脂肪酸11辅酶A',
            'fa12coa_c': '脂肪酸12辅酶A',
            'fa1coa_c': '脂肪酸1辅酶A',
            'fa3coa_c': '脂肪酸3辅酶A',
            'fa4coa_c': '脂肪酸4辅酶A',
            'fa6coa_c': '脂肪酸6辅酶A',
            'strcoa_c': '硬脂酸辅酶A',
            'coa_c': '辅酶A',
            '12dag3p_BS_c': '1,2-二酰基甘油-3-磷酸(BS特异性)'
        }
        
        mets_dict = {}
        for met_id, met_name in metabolites.items():
            if met_id not in model.metabolites:
                print(f"创建新的代谢物: {met_id}")
                new_met = cobra.Metabolite(
                    met_id,
                    name=met_name,
                    compartment='c'
                )
                model.add_metabolites([new_met])
                mets_dict[met_id] = new_met
            else:
                mets_dict[met_id] = model.metabolites.get_by_id(met_id)
        
        # 设置反应
        reaction.add_metabolites({
            mets_dict['pmtcoa_c']: -10,
            mets_dict['tdcoa_c']: -3,
            mets_dict['1ag3p_BS_c']: -1,
            mets_dict['fa11coa_c']: -7,
            mets_dict['fa12coa_c']: -17,
            mets_dict['fa1coa_c']: -1,
            mets_dict['fa3coa_c']: -20,
            mets_dict['fa4coa_c']: -34,
            mets_dict['fa6coa_c']: -5,
            mets_dict['strcoa_c']: -3,
            mets_dict['coa_c']: 1,
            mets_dict['12dag3p_BS_c']: 1
        })
        
        # 设置可逆性
        reaction.lower_bound = -1000  # 可逆反应
        reaction.upper_bound = 1000
        
        print(f"添加/更新后的反应: {reaction.build_reaction_string()}")
        return True
    except Exception as e:
        print(f"添加AGPATr_BS反应时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def add_man6gpts_reaction(model):
    """
    添加MAN6Gpts反应: h2o_c + pep_c + man6pglyc_e --> man6pglyc_c + pi_c + pyr_c
    """
    print("添加MAN6Gpts反应...")
    
    try:
        # 检查反应是否已存在
        if 'MAN6Gpts' in model.reactions:
            reaction = model.reactions.get_by_id('MAN6Gpts')
            print(f"反应MAN6Gpts已存在，将更新: {reaction.build_reaction_string()}")
            # 清除所有代谢物
            reaction.subtract_metabolites(reaction.metabolites)
        else:
            # 创建新反应
            reaction = cobra.Reaction('MAN6Gpts')
            reaction.name = "mannose-6-phosphate group transporter via PEP:Pyr PTS"
            reaction.subsystem = "Transport"
            model.add_reactions([reaction])
            print("创建新反应MAN6Gpts")
        
        # 确保所有代谢物存在
        metabolites = {
            'h2o_c': '水',
            'pep_c': '磷酸烯醇式丙酮酸',
            'man6pglyc_e': '甘露糖-6-磷酸(胞外)',
            'man6pglyc_c': '甘露糖-6-磷酸(胞内)',
            'pi_c': '无机磷酸盐',
            'pyr_c': '丙酮酸'
        }
        
        mets_dict = {}
        for met_id, met_name in metabolites.items():
            if met_id not in model.metabolites:
                print(f"创建新的代谢物: {met_id}")
                new_met = cobra.Metabolite(
                    met_id,
                    name=met_name,
                    compartment=met_id[-1]  # 使用ID的最后一个字符作为区室
                )
                model.add_metabolites([new_met])
                mets_dict[met_id] = new_met
            else:
                mets_dict[met_id] = model.metabolites.get_by_id(met_id)
        
        # 设置反应
        reaction.add_metabolites({
            mets_dict['h2o_c']: -1,
            mets_dict['pep_c']: -1,
            mets_dict['man6pglyc_e']: -1,
            mets_dict['man6pglyc_c']: 1,
            mets_dict['pi_c']: 1,
            mets_dict['pyr_c']: 1
        })
        
        # 设置为不可逆
        reaction.lower_bound = 0
        reaction.upper_bound = 1000
        
        print(f"添加/更新后的反应: {reaction.build_reaction_string()}")
        return True
    except Exception as e:
        print(f"添加MAN6Gpts反应时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def run_memote(model_file):
    """
    运行memote生成报告
    """
    print(f"运行memote分析模型文件: {model_file}")
    
    # 生成报告文件名
    report_file = os.path.splitext(model_file)[0] + "_memote_report.html"
    
    try:
        # 运行memote命令生成报告
        cmd = f"/opt/homebrew/bin/python3.11 -m memote report snapshot --filename {report_file} {model_file}"
        print(f"执行命令: {cmd}")
        
        # 使用subprocess执行memote命令
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if process.returncode == 0:
            print(f"Memote报告已生成: {report_file}")
            print(process.stdout)
            return True
        else:
            print(f"Memote报告生成失败，错误信息:")
            print(process.stderr)
            return False
    
    except Exception as e:
        print(f"运行memote时出错: {str(e)}")
        return False

def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python apply_reaction_fix.py <输入模型文件> [输出模型文件]")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "updated_model.xml"
    
    try:
        # 加载模型
        print(f"加载模型文件: {input_file}")
        model = cobra.io.read_sbml_model(input_file)
        
        # 应用反应修改
        cmcbtfl_updated = update_cmcbtfl_reaction(model)
        salchs4feabcpp_updated = update_salchs4feabcpp_reaction(model)
        
        # 添加新反应
        agpatr_bs_added = add_agpatr_bs_reaction(model)
        man6gpts_added = add_man6gpts_reaction(model)
        
        if cmcbtfl_updated and salchs4feabcpp_updated and agpatr_bs_added and man6gpts_added:
            # 保存更新的模型
            print(f"保存更新后的模型到: {output_file}")
            cobra.io.write_sbml_model(model, output_file)
            
            # 运行memote生成报告
            run_memote(output_file)
        else:
            print("修改或添加反应失败，未保存模型")
    
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 