# Name:      lokai/lk_worker/nodes/graph.py
# Purpose:   Support the directed graph data structure
# Copyright: 2011: Database Associates Ltd.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
#    See the License for the specific language governing permissions and
#    limitations under the License.

#-----------------------------------------------------------------------

""" Interface routines:

    make_link - given a source node and a target node, link the source
        as a child under the target and update the parent manifest for
        the source sub-tree.

    make_unlink - given a source node and a target node, unlink the
        source from the target and update the parent manifest for the
        source sub-tree.

    search_down - given a query and a set of sub-tree starting nodes,
        apply the query to the sub-trees. Return either the full
        result or the top level results from a depth first search.

    top_trees - identify all the nodes that do not have parents.
"""

#-----------------------------------------------------------------------

from sqlalchemy.sql import exists, not_, or_, and_, select, text, func
from sqlalchemy.orm import exc as orm_exc

from lokai.tool_box.tb_database.orm_interface import engine

from lokai.lk_worker.models import ndNode, ndEdge, ndParent

from lokai.lk_worker import (ndGraphCycle, ndLinkMissing)

#-----------------------------------------------------------------------

def is_cycle(source, target):
    """Check to see if linking source to target would lead to a cycle
    """
    if (source == target or
        engine.session.query(ndParent).filter(
            or_(and_(ndParent.nde_idx == source,
                     ndParent.nde_parent == target),
                and_(ndParent.nde_idx == target,
                     ndParent.nde_parent == source))).first()
        ):
        return True
    return False

def make_link(source, target, query_test=False):
    """Create edge entries linking source to target.

       srource = idx for child
       target = idx for parent
       
       Use the parent manifest for the target and merge it into the
       parent manifest for the entire sub-tree from the source
       downwards.
    """

    # Reject if this leads to a cycle
    
    if is_cycle(source, target):
        raise ndGraphCycle(
            "source=%s, target=%s" % (source, target))

    # Get the next sequence number
    sequence_response = engine.session.query(
        func.max(ndEdge.nde_sequence).label('max_sequence_value')
        ).filter(
        ndEdge.nde_parent == target).first()
    sequence_position = 0
    if sequence_response and sequence_response.max_sequence_value is not None:
        sequence_position = sequence_response.max_sequence_value + 1
    # insert the new edge
    nd_edge = ndEdge()
    nd_edge.nde_child = source
    nd_edge.nde_parent = target
    nd_edge.nde_sequence = sequence_position
    engine.session.add(nd_edge)

    # Update the parent manifest
    #
    # INSERT INTO p SELECT * 
    #           FROM (SELECT node, parent 
    #                FROM (SELECT DISTINCT node FROM p 
    #                      WHERE p.parent = source 
    #                      UNION SELECT source ) as node_select,
    #                    (SELECT parent FROM p
    #                     WHERE p.node = target
    #                     UNION SELECT target ) as parent_select
    #                 ) as insert_select
    #           WHERE NOT EXISTS (SELECT * FROM p AS py
    #                                     WHERE py.node = insert_select.node
    #                                     AND py.parent = insert_select.parent )
    nd_parent = ndParent().get_mapped_table()

    node_select = select(columns=[nd_parent.c.nde_idx]).where(
        nd_parent.c.nde_parent == source).union(
        select(columns=["'%s'"%source])).alias()

    parent_select = select(columns=[nd_parent.c.nde_parent]).where(
        nd_parent.c.nde_idx == target).union(
        select(columns=["'%s'"%target])).alias()

    insert_select = select([node_select, parent_select]).alias()
    
    value_select = select([insert_select]).where(
        not_(exists(['*']).where(
            and_(nd_parent.c.nde_idx == insert_select.c.nde_idx,
                 nd_parent.c.nde_parent == insert_select.c.nde_parent)
                 )
            ))

    # Problem with SQL Alchemy, it does not support INSERT ... SELECT.
    # We have to create a text version of the SQL 
    value_select_string = str(value_select)%{'nde_parent_1':"'%s'"%source,
                                             'nde_idx_1':"'%s'"%target}
    if query_test:
        value_op = engine.session.execute(text(value_select_string),
                                          mapper=ndParent)
        
    insert_parent = text("INSERT INTO nd_parent "+value_select_string)

    engine.session.execute(insert_parent, mapper=ndParent)
    #
    # Force out the new edge so that the nde_sequence value can be found.
    engine.session.flush()
    
    if query_test:
        return value_op
    
#-----------------------------------------------------------------------

def make_unlink(source, target, query_test=False):
    """Remove edge entries linking source to target.

       Remove redundant entries from parent manifest by a
       breadth-first pass through the sub-tree based on the source
       node.

       At each level, the parent manifest of a child node is the
       merged sum of the parent manifests, plus the parents themselves
    """
    #
    # Check there really is a link to break
    lnk = engine.session.query(ndEdge).filter(
        and_(ndEdge.nde_child == source,
             ndEdge.nde_parent == target)).first()
    if not lnk:
        raise ndLinkMissing(
            "%s to %s"% (source, target))
    #
    # Remove the edge
    nd_edge = ndEdge().get_mapped_table()
    dlt = nd_edge.delete().where(
        and_(nd_edge.c.nde_child == source,
             nd_edge.c.nde_parent == target))
    engine.session.execute(dlt, mapper=ndEdge)
    #
    # Breadth-first search
    nd_parent = ndParent().get_mapped_table()
    node_queue = [source]
    while node_queue:
        here = node_queue.pop(0)
        #
        # Rebuild the parent manifest for here
        delete_parents = nd_parent.delete().where(
            nd_parent.c.nde_idx == here)
        engine.session.execute(delete_parents, mapper=ndParent)
        manifest_select = engine.session.query(ndParent.nde_parent).filter(
            and_(ndParent.nde_idx == ndEdge.nde_parent,
                 ndEdge.nde_child == here))
        edge_select = engine.session.query(ndEdge.nde_parent).filter(
            ndEdge.nde_child == here)
        parent_select = manifest_select.union(edge_select)

        manifest_insert_base = text(
            "SELECT %(nde_child_0)s, * FROM (%(parent_set)s) AS px"%{
                'nde_child_0': "'%s'"%here,
                'parent_set': str(parent_select.statement)%{
                    'nde_child_1': "'%s'"%here,
                    'nde_child_2': "'%s'"%here}
                }
            )

        insert_sql = text("INSERT INTO nd_parent " + str(manifest_insert_base))
        engine.session.execute(insert_sql, mapper=ndParent)
        #
        # Add children to the queue
        child_select = select(
            columns=[nd_edge.c.nde_child]).where(
            nd_edge.c.nde_parent == here)
        child_set = engine.session.execute(child_select, mapper=ndEdge)
        for child_row in child_set:
            #
            # Add child to queue
            child = child_row[0]
            node_queue.append(child)

#-----------------------------------------------------------------------

def top_trees():
    """Return a list of nodes that have no parents
    """
    nd_edge = ndEdge().get_mapped_table()
    nd_node = ndNode().get_mapped_table()
    node_select = nd_node.select().where(
        not_(exists().where(nd_edge.c.nde_child == nd_node.c.nde_idx)))

    node_set = engine.session.execute(node_select, mapper=ndNode)

    op = []
    for node in node_set:
        op.append(node[0])

    return op

#-----------------------------------------------------------------------

def child_trees(tops=[]):
    """Return a list of nodes that are the child nodes of tops.
    """
    if not tops:
        tops = top_trees()
    else:
        if isinstance(tops, (type(''), type(u''))):
            tops = [tops]
    edge_search = engine.session.query(ndEdge).filter(
        ndEdge.nde_parent.in_(tops))
    edge_set = edge_search.all()
    op = []
    for result in edge_set:
        op.append(result.nde_child)

    return op

#-----------------------------------------------------------------------

class NodeFamily(object):
    """ Find the parents and all the siblings for this node.

        If a node is given, the parents are the parents of this node
        and the siblings are the siblings of this node. If also a
        parent is given then this is used as the preferred parent in
        the parent list. (The preferred parent appears first in the
        list of parents.)

        If a node is not given, siblings_left contains all the
        children of the given parent, while siblings_right is empty.

        The returned elements are tuples, or lists of ndNode
        
        :family.parents: List of all the parents of the node. If a
            `node` is given and there are multiple parents then the
            first parent in the list is either: the `parent` node, if
            given; or the parent on the node edge where nde_choice is
            True; or simply the first in whatever order the database
            returns.

        :family.siblings_left: All the siblings of the given node that
            are less than the given node in the assumed sort order.

        :family.siblings_me: The given node. Empty if no `node` given.

        :family.siblings_right: All the siblings of the given node that
            are greater than the given node in the assumed sort order.

    """

    def __init__(self, node=None, parent=None, **kwargs):
        """ kwargs:

            :order: String. Field name to be used for ordering the
                siblings.

                The field name should belong to one of:

                    ndEdge

                    ndNode

                    The object defined in `sort_object`.

                If the field name is in ndNode or NdEdge than
                `sort_object` is not required. The code uses whichever
                object has the given field as an attribute.

                ndNode.nde_idx is always used as a secondary ordering.

            :sort_object: Database object. A database object that
                contains the field attribute defined in `order`.

            :flow: String. 'ASC' or 'DSC' - default 'ASC'
            
        """
        self.siblings_left = []
        self.siblings_right = []
        self.siblings_me = None
        self.parents = []
        self.up = None
        if parent is not None and parent.strip() != '':
            self.up = parent.strip()
        self.node = node

        self.flow = kwargs.get('flow', None)
        self.order = kwargs.get('order', 'nde_sequence')
        self.sort_obj = kwargs.get('sort_object', None)
        if self.order and not self.sort_obj:
            if self.order in ndEdge():
                 self.sort_obj = ndEdge
            elif self.order in ndNode():
                self.sort_obj = ndNode
            else:
                assert self.sort_obj, ("A sort object must be findable "
                                       "if sort order given")

        if self.node is not None and self.node != '**new**':
            #
            # Look for parents
            self._find_the_parents(self.node)
        else:
            if self.up is not None:
                qp = (engine.session.query
                  (ndNode).filter
                  (ndNode.nde_idx == self.up))
                try:
                    edge = qp.one()
                except orm_exc.NoResultFound:
                    raise ndNodeMissing( 
                        "Can't find node %s"%(self.up))   
                self.parents = [edge]
            
        try:
            nde_up = self.parents[0].nde_idx
        except IndexError:
            nde_up = None
            
        if nde_up is not None:
            self._find_the_siblings(nde_up)

    def _find_the_parents(self, nde_here):
        """ Search the given node to find immediate parents
        """
        qp = (engine.session.query
              (ndEdge, ndNode).join
              ((ndNode,  ndEdge.nde_parent == ndNode.nde_idx)).filter
              (ndEdge.nde_child == nde_here))
        qp_set = qp.all()
        #
        # List of tuples (ndEdge, ndNode)
        for edge in qp_set:
            if ((self.up and edge[0].nde_parent == self.up) or
                (not self.up and edge[0].nde_choice)):
                #
                # Make sure this is first
                if len(self.parents):
                    self.parents.insert(0, edge[1])
                else:
                    self.parents.append(edge[1])
            else:
                self.parents.append(edge[1])

    def _find_the_siblings(self, nde_up):
        """ Extract the children of the given node.
        """
        qs = (engine.session.query
              (ndNode).join
              ((ndEdge,  ndEdge.nde_child == ndNode.nde_idx)).filter
              (ndEdge.nde_parent == nde_up))
        if self.order:
            if self.flow == 'DSC':
                qs = qs.order_by(getattr(self.sort_obj, self.order).desc())
            else:
                qs = qs.order_by(getattr(self.sort_obj, self.order).asc())
        if self.order != ndNode:
            # Add a default sub-ordering
            if self.flow == 'DSC':
                qs = qs.order_by(ndNode.nde_idx.desc())
            else:
                qs = qs.order_by(ndNode.nde_idx.asc())
        qs_set = qs.all()

        switch = False
        #
        # List of ndNode
        for edge in qs_set:
            child = edge.nde_idx
            if self.node and child == self.node:
                switch = not switch
                self.siblings_me = edge
            else:
                if switch:
                    self.siblings_right.append(edge)
                else:
                    self.siblings_left.append(edge)
        
    def __str__(self):
        op = []
        op.append("Node       %s"%str(self.node))
        op.append("Parents    %s"%str(self.parents))
        op.append("Left sibs  %s"%str(self.siblings_left))
        op.append("Right sibs %s"%str(self.siblings_right))
        return '\n'.join(op)

#-----------------------------------------------------------------------
