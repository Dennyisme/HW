#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum { RED, BLACK } NodeColor;

typedef struct RBTreeNode {
    int data;
    NodeColor color;
    struct RBTreeNode *left;
    struct RBTreeNode *right;
    struct RBTreeNode *parent;
} RBTreeNode;

typedef struct RBTree {
    RBTreeNode* root;
    RBTreeNode* nil;
} RBTree;

// 函數來創建一個新節點
RBTreeNode* create_node(int data) {
    RBTreeNode *newNode = (RBTreeNode*)malloc(sizeof(RBTreeNode));
    if (newNode) {
        newNode->data = data;
        newNode->color = RED;  // 新節點默認設為紅色
        newNode->left = NULL;
        newNode->right = NULL;
        newNode->parent = NULL;
    }
    return newNode;
}

RBTree* create_tree() {
    RBTree* t = (RBTree*)malloc(sizeof(RBTree));
    if (t) {
        t->nil = (RBTreeNode*)malloc(sizeof(RBTreeNode));
        if (t->nil) {
            t->nil->color = BLACK;
            t->nil->left = t->nil->right = t->nil->parent = t->nil;
        }
        t->root = t->nil;
    }
    return t;
}

void leftRotate(RBTree *t, RBTreeNode *x) {
    RBTreeNode *y = x->right; // 設定 y 為 x 的右子節點
    // 將 y 的左子節點移至 x 的右子節點
    x->right = y->left;
    if (y->left != t->nil) {
        y->left->parent = x;
    }
    // 更新父節點的指針
    y->parent = x->parent;
    if (x->parent == t->nil) { // x 是根節點
        t->root = y;
    } else if (x == x->parent->left) { // x 是其父節點的左子節點
        x->parent->left = y;
    } else { // x 是其父節點的右子節點
        x->parent->right = y;
    }
    // 將 x 設為 y 的左子節點
    y->left = x;
    x->parent = y;
}

void rightRotate(RBTree *t, RBTreeNode *y) {
    RBTreeNode *x = y->left; // 設定 x 為 y 的左子節點
    // 將 x 的右子節點移至 y 的左子節點
    y->left = x->right;
    if (x->right != t->nil) {
        x->right->parent = y;
    }
    // 更新父節點的指針
    x->parent = y->parent;
    if (y->parent == t->nil) { // y 是根節點
        t->root = x;
    } else if (y == y->parent->left) { // y 是其父節點的左子節點
        y->parent->left = x;
    } else { // y 是其父節點的右子節點
        y->parent->right = x;
    }
    // 將 y 設為 x 的右子節點
    x->right = y;
    y->parent = x;
}

RBTreeNode *search(RBTree *t, int key) {
    RBTreeNode *node = t->root;
	while (node != t->nil) {
		if (key < node->data) {
			node = node->left;
		}
		else if (key > node->data) {
			node = node->right;
		}
		else {
			return node;
		}
	}
	return t->nil;
}

// rbtree_insert_fixup 函數用於在插入新節點後修復紅黑樹的性質。
void insert_fixup(RBTree *t, RBTreeNode *z) {
    // 當新插入節點的父節點為紅色時進行調整
    while (z->parent->color == RED) {
        // 判斷父節點是位於祖父節點的左邊還是右邊
        if (z->parent == z->parent->parent->left) {
            // 父節點在左邊
            RBTreeNode *y = z->parent->parent->right; // 叔叔節點
            if (y->color == RED) {
                // 叔叔節點為紅色，進行顏色調整
                y->color = BLACK;
                z->parent->color = BLACK;
                z->parent->parent->color = RED;
                z = z->parent->parent;
            } else {
                // 叔叔節點為黑色或NIL
                if (z->parent->right == z) {
                    // 新節點為右子節點，進行左旋
                    z = z->parent;
                    leftRotate(t, z);
                }
                // 調整顏色並進行右旋
                z->parent->color = BLACK;
                z->parent->parent->color = RED;
                rightRotate(t, z->parent->parent);
            }
        } else {
            // 父節點在右邊，處理邏輯與左邊類似，方向相反
            RBTreeNode *y = z->parent->parent->left; // 叔叔節點
            if (y->color == RED) {
                // 叔叔節點為紅色，進行顏色調整
                z->parent->parent->color = RED;
                z->parent->color = BLACK;
                y->color = BLACK;
                z = z->parent->parent;
            } else {
                if (z == z->parent->left) {
                    // 新節點為左子節點，進行右旋
                    z = z->parent;
                    rightRotate(t, z);
                }
                // 調整顏色並進行左旋
                z->parent->color = BLACK;
                z->parent->parent->color = RED;
                leftRotate(t, z->parent->parent);
            }
        }
    }
    // 確保根節點始終為黑色
    t->root->color = BLACK;
}

// rbtree_insert 函數用於將一個新節點插入紅黑樹。
void insert(RBTree *t, RBTreeNode *z) {
    RBTreeNode *pre = t->nil; // 初始化指針
    RBTreeNode *cur = t->root;
    // 尋找合適的插入位置
    while (cur != t->nil) {
        pre = cur;
        if (z->data > cur->data)
            cur = cur->right;
        else if (z->data < cur->data)
            cur = cur->left;
        else
            return; // 如果已存在相同鍵值，則不插入
    }
    // 設置新節點的父節點
    z->parent = pre;
    if (pre == t->nil) {
        // 樹為空，設置新節點為根節點
        t->root = z;
    } else {
        if (pre->data > z->data)
            pre->left = z;
        else
            pre->right = z;
    }
    // 初始化新節點的子節點
    z->left = t->nil;
    z->right = t->nil;
    // 新節點初始設為紅色
    z->color = RED;
    // 調用修復函數修復可能的紅黑樹性質違反
    insert_fixup(t, z);
}

// rbtree_mini 函數用於尋找給定節點的最小值節點
RBTreeNode *mini(RBTree *t, RBTreeNode *x) {
    // 循環直到找到最左邊的節點（即最小值節點）
    while (x->left != t->nil) {
        x = x->left;
    }
    return x; // 返回最小值節點
}

// rbtree_maxi 函數用於尋找給定節點的最大值節點
RBTreeNode *maxi(RBTree *t, RBTreeNode *x) {
    // 循環直到找到最右邊的節點（即最大值節點）
    while (x->right != t->nil) {
        x = x->right;
    }
    return x; // 返回最大值節點
}

// rbtree_successor 函數用於尋找給定節點的後繼者
RBTreeNode *successor(RBTree *t, RBTreeNode *x) {
    // y 用於追蹤 x 的父節點
    RBTreeNode *y = x->parent;

    // 如果 x 有右子節點，則 x 的後繼者是其右子樹中的最小值節點
    if (x->right != t->nil) {
        return mini(t, x->right);
    }

    // 如果 x 沒有右子節點，則沿父節點路徑向上尋找，
    // 直到找到一個節點是其父節點的左子節點
    while ((y != t->nil) && (x == y->right)) {
        x = y; // 移動到父節點
        y = y->parent; // 更新 y 為父節點的父節點
    }

    // 返回後繼者
    return y;
}


// rbtree_delete_fixup 函數用於在刪除節點後修復紅黑樹的性質。
void delete_fixup(RBTree *t, RBTreeNode *x) {
    // 當 x 不是根節點且為黑色時循環
    while ((x != t->root) && (x->color == BLACK)) {
        // 判斷 x 是左子節點還是右子節點
        if (x == x->parent->left) {
            // x 是左子節點
            RBTreeNode *w = x->parent->right; // w 為 x 的兄弟節點
            if (w->color == RED) {
                // 如果兄弟節點為紅色
                w->color = BLACK; // 將兄弟節點設為黑色
                x->parent->color = RED; // 將父節點設為紅色
                leftRotate(t, x->parent); // 對父節點進行左旋
                w = x->parent->right; // 重新設置 w 為 x 的兄弟節點
            }
            // 檢查 w 的子節點的顏色
            if ((w->left->color == BLACK) && (w->right->color == BLACK)) {
                // 如果 w 的兩個子節點都是黑色
                w->color = RED; // 將 w 設為紅色
                x = x->parent; // 將 x 設為其父節點
            } else {
                // w 至少有一個紅色子節點
                if (w->right->color == BLACK) {
                    // 如果 w 的右子節點是黑色
                    w->left->color = BLACK; // 將 w 的左子節點設為黑色
                    w->color = RED; // 將 w 設為紅色
                    rightRotate(t, w); // 對 w 進行右旋
                    w = x->parent->right; // 重新設置 w 為 x 的兄弟節點
                }
                // 將 w 的顏色設為與其父節點相同
                w->color = x->parent->color;
                x->parent->color = BLACK; // 將 x 的父節點設為黑色
                w->right->color = BLACK; // 將 w 的右子節點設為黑色
                leftRotate(t, x->parent); // 對 x 的父節點進行左旋
                x = t->root; // 將 x 設為根節點
            }
        } else {
            // x 是右子節點，處理邏輯與 x 為左子節點相反
            RBTreeNode *w = x->parent->left; // w 為 x 的兄弟節點
            if (w->color == RED) {
                // 如果兄弟節點為紅色
                w->color = BLACK; // 將兄弟節點設為黑色
                x->parent->color = RED; // 將父節點設為紅色
                rightRotate(t, x->parent); // 對父節點進行右旋
                w = x->parent->left; // 重新設置 w 為 x 的兄弟節點
            }
            // 檢查 w 的子節點的顏色
            if ((w->left->color == BLACK) && (w->right->color == BLACK)) {
                // 如果 w 的兩個子節點都是黑色
                w->color = RED; // 將 w 設為紅色
                x = x->parent; // 將 x 設為其父節點
            } else {
                // w 至少有一個紅色子節點
                if (w->left->color == BLACK) {
                    // 如果 w 的左子節點是黑色
                    w->right->color = BLACK; // 將 w 的右子節點設為黑色
                    w->color = RED; // 將 w 設為紅色
                    leftRotate(t, w); // 對 w 進行左旋
                    w = x->parent->left; // 重新設置 w 為 x 的兄弟節點
                }
                // 將 w 的顏色設為與其父節點相同
                w->color = x->parent->color;
                x->parent->color = BLACK; // 將 x 的父節點設為黑色
                w->left->color = BLACK; // 將 w 的左子節點設為黑色
                rightRotate(t, x->parent); // 對 x 的父節點進行右旋
                x = t->root; // 將 x 設為根節點
            }
        }
    }
    // 將 x 設為黑色以恢復紅黑樹性質
    x->color = BLACK;
}

// rbtree_delete 函數用於從紅黑樹中刪除節點 z。
void delete(RBTree *t, RBTreeNode *z) {
    RBTreeNode *y = t->nil; // y 將成為被移除或移動的節點
    RBTreeNode *x = t->nil; // x 將是 y 的替代節點

    // 決定要移除的節點是 z 還是其後繼者
    if ((z->left == t->nil) || (z->right == t->nil)) {
        // 如果 z 至少有一個 NIL 子節點
        y = z;
    } else {
        // 找到 z 的後繼者
        y = successor(t, z);
    }

    // 確定 y 的替代節點 x
    if (y->left != t->nil)
        x = y->left;
    else if (y->right != t->nil)
        x = y->right;

    // 將 x 的父節點設為 y 的父節點
    x->parent = y->parent;
    // 如果 y 是根節點，則將 x 設為根節點
    if (y->parent == t->nil)
        t->root = x;
    // 否則，根據 y 是左還是右子節點來更新父節點的子節點
    else if (y == y->parent->left)
        y->parent->left = x;
    else
        y->parent->right = x;

    // 如果 y 不是 z，則將 y 的數據複製到 z
    if (y != z) {
        z->data = y->data;
    }

    // 如果 y 是黑色，則需要進行修復，因為刪除黑色節點可能會破壞紅黑樹性質
    if (y->color == BLACK) {
        delete_fixup(t, x);
    }
}

int main(int argc, char* argv[]) {
    RBTree *t = create_tree();
    char command[100];
    int x;
    while(scanf("%s", command) != EOF) {
        if (strcmp(command, "insert") == 0) {
            if (scanf("%d", &x) != 1) {
                fprintf(stderr, "Insert input error.\n");
                continue;
            }
            RBTreeNode* newNode = create_node(x);
            insert(t, newNode);
        } else if (strcmp(command, "delete") == 0) {
            if (scanf("%d", &x) != 1) {
                fprintf(stderr, "Delete input error.\n");
                continue;
            }
            RBTreeNode* delNode = search(t, x);
            if (delNode != t->nil) {
                delete(t, delNode);
            }
        } else if (strcmp(command, "search") == 0) {
            if (scanf("%d", &x) != 1) {
                fprintf(stderr, "Search input error.\n");
                continue;
            }
            RBTreeNode* node = search(t, x);
            if (node != t->nil) {
                printf("%s\n", node->color == RED ? "red" : "black");
            } else {
                printf("Not found\n");
            }
        } else if (strcmp(command, "quit") == 0) {
            break;
        }
    }
    free(t);
    return 0;
}
