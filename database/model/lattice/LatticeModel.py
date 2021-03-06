from typing import List, Set

from database.model.graph_base.GraphModel import GraphModel
from database.model.lattice.ConceptNodeModel import ConceptNodeModel


class LatticeModel(GraphModel):
    def __init__(self, label):
        # 继承父类方法
        GraphModel.__init__(self, label=label, relationship_name="child")
        self._label = label
        self._relationship_name = "child"

    # 添加一个节点
    def add_node(self, concept: ConceptNodeModel = None):
        if concept:
            node_id = super(LatticeModel, self).add_node(extents=concept.extents, intents=concept.intents)
        else:
            node_id = super(LatticeModel, self).add_node()
        concept.id = node_id

    # 根据ID取节点信息
    def get_node_base_on_id(self, node_id: int) -> ConceptNodeModel:
        node_info = super(LatticeModel, self).get_node_base_on_id(node_id)
        # 去除两边两侧双引号
        extents = node_info['extents']
        intents = node_info['intents']
        for i, extent in enumerate(extents):
            extents[i] = extent.strip('\"')
        for i, intent in enumerate(intents):
            intents[i] = intent.strip('\"')
        node = ConceptNodeModel(node_id=node_info.id, extents=set(extents),
                                intents=set(intents))
        return node

    # 更新节点的属性值
    def update_node_property(self, node_id: int, **properties):
        super(LatticeModel, self).update_node_property(node_id, **properties)

    # 删除节点的属性
    def remove_node_property(self, node_id: int, property_name):
        super(LatticeModel, self).remove_node_property(node_id, property_name)

    # 删除一个节点及其相关边
    def delete_node(self, delete_node_id: int):
        super(LatticeModel, self).delete_node(delete_node_id)

    # 添加一条边
    def add_edge(self, node_id_from: int, node_id_to: int):
        super(LatticeModel, self).add_edge(node_id_from=node_id_from, node_id_to=node_id_to)

    # 删除一条边
    def remove_edge(self, node_id_from: int, node_id_to: int):
        super(LatticeModel, self).remove_edge(node_id_from=node_id_from, node_id_to=node_id_to)

    # 取节点的所有孩子节点
    def get_children(self, parent_node_id: int):
        return super(LatticeModel, self).get_children(node_id_from=parent_node_id)

    # 取节点的所有父亲节点
    def get_parents(self, node_id_to: int):
        return super(LatticeModel, self).get_parents(node_id_to=node_id_to)

    # 取所有节点内涵势排序id生成器
    def get_node_id_order_by_intents_length(self):
        return super(LatticeModel, self).get_node_order('length(n.intents)')

    # 取所有节点内涵势逆序排序id生成器
    def get_node_id_order_by_intents_length_desc(self):
        return super(LatticeModel, self).get_node_order_desc('length(n.intents)')

    def get_node_count(self) -> int:
        """取节点数量"""
        return super(LatticeModel, self).get_node_count()

    def set_sup_node(self, node_id: int = -1):
        """将节点置为sup节点,若不指定id,则入度为0的节点为sup节点"""
        if node_id != -1:
            super(LatticeModel, self).add_node_property(node_id=node_id, is_sup=True)
        else:
            statement = "match (n:{}) with n,size(()-[:{}]->(n)) as InDepth where InDepth=0 set n.is_sup = True return n limit 1".format(
                self._label, self._relationship_name)
            super(LatticeModel, self).run_statement_without_return(statement)

    def set_inf_node(self, node_id: int = -1):
        """将节点置为inf节点,若不指定id,则出度为0的节点为inf节点"""
        if node_id != -1:
            super(LatticeModel, self).add_node_property(node_id=node_id, is_inf=True)
        else:
            statement = "match (n:{}) with n,size((n)-[:{}]->()) as OutDepth where OutDepth=0 set n.is_inf = True return n limit 1".format(
                self._label, self._relationship_name)
            super(LatticeModel, self).run_statement_without_return(statement)

    def get_sup_node(self)->ConceptNodeModel:
        """取sup节点"""
        node_info = super(LatticeModel, self).get_node_base_on_property(property_name="is_sup", value=True,
                                                                        limit=1)
        node_info = node_info.__next__()
        extents = set(node_info['extents']) if node_info['extents'] else set()
        intents = set(node_info['intents']) if node_info['intents'] else set()
        node = ConceptNodeModel(node_id=node_info.id, extents=extents, intents=intents)
        return node

    def get_inf_node(self)->ConceptNodeModel:
        """取inf节点"""
        node_info = super(LatticeModel, self).get_node_base_on_property(property_name="is_inf", value=True,
                                                                        limit=1)
        node_info = node_info.__next__()
        extents = set(node_info['extents']) if node_info['extents'] else set()
        intents = set(node_info['intents']) if node_info['intents'] else set()
        node = ConceptNodeModel(node_id=node_info.id, extents=extents, intents=intents)
        return node

    # 判断a是否是b父节点
    def is_parent(self, concept_a: ConceptNodeModel, concept_b: ConceptNodeModel):
        return concept_b.id in self.get_children(concept_a.id)

    # 清空所有节点
    def delete_all(self):
        super(LatticeModel, self).delete_all()

    # 概念加入集合
    @staticmethod
    def update_list(concept: ConceptNodeModel, update_list: List[Set[int]]):
        length: int = len(concept.intents)
        if length >= len(update_list):
            for i in range(length - len(update_list) + 1):
                update_list.append(set())
        update_list[length].add(concept.id)
