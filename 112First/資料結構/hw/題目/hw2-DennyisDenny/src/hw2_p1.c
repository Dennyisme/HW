#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
// #include <stdbool.h>
#ifndef __cplusplus
#define bool int
#define TRUE 1
#define FALSE 0
#endif

typedef struct node {
    int value;
    int key;
    struct node* parent;
    struct node* child;
    struct node* left;
    struct node* right;
    int degree; // 表示子節點的數量
    int mark; // 標記節點是否失去了一個子節點
} node;

typedef struct fheap {
    node* min;
    int n; // 節點的總數
} fheap;

node* create_node(int k, int val) {
    node* temp = (node*)malloc(sizeof(node));
    if (temp == NULL) {
        fprintf(stderr, "Out of memory.\n");
        exit(EXIT_FAILURE);
    }
    temp->value = val;
    temp->key = k;
    temp->degree = 0;
    temp->parent = NULL;
    temp->child = NULL;
    temp->left = temp;
    temp->right = temp;
    temp->mark = FALSE;
    return temp;
}

fheap* make_heap() {
    fheap* temp = (fheap*)malloc(sizeof(fheap));
    if (temp == NULL) {
        fprintf(stderr, "Out of memory.\n");
        exit(EXIT_FAILURE);
    }
    temp->min = NULL;
    temp->n = 0;
    return temp;
}

void addToRootList(fheap* heap, node *newNode) {
    if (heap->min == NULL) {
        heap->min = newNode; // 將新節點設為最小節點
        newNode->left = newNode;
        newNode->right = newNode;
    } else {
        newNode->right = heap->min->right;
        newNode->left = heap->min;
        heap->min->right->left = newNode;
        heap->min->right = newNode;
        // 更新最小節點指標
        if (newNode->key < heap->min->key) {
            heap->min = newNode;
        }
    }
}

void insert(fheap* heap, node *newNode) {
    addToRootList(heap, newNode);
    heap->n++;
}

void cut(fheap* heap, node* child, node* parent){
    if(parent->child == child){
        if(child->right == child)
            parent->child = NULL;
        else
            parent->child = child->right;
    }
    if(parent->child != NULL){
        child->right->left = child->left;
        child->left->right = child->right;
    }
    addToRootList(heap, child);
    child->parent = NULL;
    child->mark = FALSE;
    parent->degree--;
}

void cascading_cut(fheap* heap, node* n)
{
    node* parent = n->parent;
    if(parent != NULL)
    {
        if(n->mark == FALSE)
            n->mark = TRUE;
        else
        {
            cut(heap, n, parent);
            cascading_cut(heap, parent);
        }
    }
}

// 將節點p2作為p1的子節點
void link(fheap* heap, node* p2, node* p1){
    (p2->left)->right = p2->right;
    (p2->right)->left = p2->left;
    if(p1->right == p1){
        heap->min = p1;
    }
    p2->left = p2;
    p2->right = p2;
    p2->parent = p1;
    if(p1->child == NULL){
        p1->child = p2;
    }else{
        p2->right = p1->child;
        p2->left = (p1->child)->left;
        ((p1->child)->left)->right = p2;
        (p1->child)->left = p2;
    }
    if(p2->key < (p1->child)->key){
        p1->child = p2;
    }
    p1->degree++;
    p2->mark = FALSE;
}

//重新組織heap，合併相同degree的tree
void consolidate(fheap* heap){
    int n = heap->n;
    node** x; //分配一個指針數組 x，用來存儲不同度數的節點
    x=(node**)malloc((n+1)*sizeof(node*));
    for(int i=0; i<=n; i++){
        x[i] = NULL;
    }
    node* temp2 = heap->min;
    node* temp1 = temp2;
    do{
        int degree = temp2->degree;
        while(x[degree] != NULL){
            node*temp3 = x[degree];
            if(temp2->key > temp3->key){
                node* temp4 = temp3;
                temp3 = temp2;
                temp2 = temp4;
            }
            link(heap, temp3, temp2);
            if(temp1 == temp3)
                temp1 = temp2;
            x[degree] = NULL;
            degree++;
        }
        x[degree] = temp2;
        temp2 = temp2->right;
    } while(temp2 != temp1);
    heap->min = NULL;
    for(int i=0; i<=n; i++){
        if(x[i] != NULL){
            if(heap->min == NULL){
                heap->min = x[i];
                x[i]->left = x[i];
                x[i]->right = x[i];
            }else{
                insert(heap, x[i]);
                if(x[i]->key < heap->min->key)
                    heap->min = x[i];
            }
        }
    }
}

node* extract_min(fheap* heap) {
    node* min = heap->min; // m 指向heap中的最小元素
    if (min != NULL) {
        // 遍歷最小元素的每個子節點，將它們加入到根列表中
        node* x = min->child;
        node* next;
        while (x != NULL) {
            next = x->right;
            if (x == next) {
                next = NULL;
            }
            // 將x從其兄弟節點中斷開，並加入根列表
            if (x->left) x->left->right = x->right;
            if (x->right) x->right->left = x->left;
            // 加入根列表
            addToRootList(heap, x);
            // 將x的父節點設置為NULL
            x->parent = NULL;
            x = next;
        }
        // 從根列表中移除min
        if (min->left) min->left->right = min->right;
        if (min->right) min->right->left = min->left;
        // 如果min是唯一的節點，則將最小指針設為NULL；否則，設為右邊的節點，並重新整理heap
        if (min == min->right) {
            heap->min = NULL;
        } else {
            heap->min = min->right;
            consolidate(heap);
        }
        heap->n--;
    }
    return min;
}

void decrease_key(fheap* heap, node* oldNode, int newKey){
    oldNode->key = oldNode->key - newKey;
    node* temp = oldNode->parent;
    if(temp != NULL && ((oldNode->key) < (temp->key))){
        cut(heap, oldNode, temp);
        cascading_cut(heap, temp);
    }
    if(oldNode->key < heap->min->key){
        heap->min = oldNode;
    }
}

void delete(fheap* heap, node* x){
    // 將節點 x 的鍵值減小到比堆中最小鍵值還要小的數字
    decrease_key(heap, x, INT_MIN);
    // 調用 extract_min 函數來刪除節點 x
    extract_min(heap);
}

node* find_in_children(node* start, int key, int val) {
    node* n = start;
    do {
        if (n->key == key && n->value == val) {
            return n;
        }
        if (n->child != NULL) {
            node* found = find_in_children(n->child, key, val);
            if (found) return found;
        }
        n = n->right;
    } while (n != start);
    return NULL;
}

node* find_node(fheap* heap, int key, int val) {
    if (heap->min == NULL) return NULL;
    node* n = heap->min;
    do {
        if (n->key == key && n->value == val) {
            return n;
        }
        if (n->child != NULL) {
            node* found = find_in_children(n->child, key, val);
            if (found) return found;
        }
        n = n->right;
    } while (n != heap->min);
    return NULL;
}


int main() {
    fheap* heap = make_heap();
    char command[100];
    int x, val, y;
    while(scanf("%s", command) != EOF) {
        if (strcmp(command, "insert") == 0) {
            if (scanf("%d %d", &x, &val) != 2) {
                fprintf(stderr, "Insert input error.\n");
                continue;
            }
            node* newNode = create_node(x, val);
            insert(heap, newNode);
        } else if (strcmp(command, "delete") == 0) {
            if (scanf("%d %d", &x, &val) != 2) {
                fprintf(stderr, "Delete input error.\n");
                continue;
            }
            node* delNode = find_node(heap, x, val);
            if (delNode != NULL) {
                delete(heap, delNode);
            }
        } else if (strcmp(command, "decrease") == 0) {
            if (scanf("%d %d %d", &x, &val, &y) != 3) {
                fprintf(stderr, "Decrease input error.\n");
                continue;
            }
            node* decNode = find_node(heap, x, val);
            if (decNode != NULL) {
                decrease_key(heap, decNode, y);
            }
        } else if (strcmp(command, "extract") == 0) {
            node* minNode = extract_min(heap);
            if (minNode != NULL) {
                printf("(%d)%d\n", minNode->key, minNode->value);
                free(minNode);
            }
        } else if (strcmp(command, "quit") == 0) {
            break;
        }
    }
    free(heap);
    return 0;
}
