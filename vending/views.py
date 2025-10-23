from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Product, Transaction, DenominationLog
from django.utils import timezone
import json

def vending_machine(request):
    cakes = Product.objects.filter(product_type='CAKE')
    chocolates = Product.objects.filter(product_type='CHOCOLATE')
    drinks = Product.objects.filter(product_type='DRINK')
    
    context = {
        'cakes': cakes,
        'chocolates': chocolates,
        'drinks': drinks,
    }
    return render(request, 'vending/machine.html', context)

def process_purchase(request):
    if request.method == 'POST':
        try:
            print("=== PURCHASE REQUEST STARTED ===")
            
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            denominations_data = request.POST.get('denominations', '{}')
            
            print(f"Product ID: {product_id}")
            print(f"Quantity: {quantity}")
            print(f"Denominations data: {denominations_data}")
            
            # Check if we have any products in database
            total_products = Product.objects.count()
            print(f"Total products in database: {total_products}")
            
            if total_products == 0:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'No products available in database! Please add products first.'
                })
            
            # Parse denominations
            denominations = json.loads(denominations_data)
            print(f"Parsed denominations: {denominations}")
            
            # Get product
            try:
                product = Product.objects.get(product_id=product_id)
                print(f"Product found: {product.name}, Price: {product.price}, Stock: {product.quantity}")
            except Product.DoesNotExist:
                print(f"Product with ID {product_id} not found!")
                # List available products for debugging
                available_products = Product.objects.all()
                print("Available products:")
                for p in available_products:
                    print(f"  - {p.product_id}: {p.name} (Rs {p.price})")
                
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Product not found! Available products: {list(available_products.values_list("product_id", flat=True))}'
                })
            
            # Calculate required amount (in rupees, not cents)
            required_amount = float(product.price * quantity)
            print(f"Required amount: {required_amount}")
            
            # Calculate inserted amount (in rupees)
            inserted_amount = 0
            for denom, count in denominations.items():
                inserted_amount += int(denom) * int(count)
            print(f"Inserted amount: {inserted_amount}")
            
            # Check if enough money inserted
            if inserted_amount < required_amount:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Insufficient funds! Required: Rs {required_amount:.2f}, Inserted: Rs {inserted_amount:.2f}'
                })
            
            # Check stock
            if product.quantity < quantity:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Not enough stock! Available: {product.quantity}'
                })
            
            # Calculate change
            change = inserted_amount - required_amount
            print(f"Change to return: {change}")
            
            # Update product quantity
            product.quantity -= quantity
            product.save()
            print(f"Updated product stock: {product.quantity}")
            
            # Create transaction
            transaction = Transaction.objects.create(
                total_amount_inserted=inserted_amount,
                amount_required=required_amount,
                change_returned=change
            )
            print(f"Transaction created: {transaction.id}")
            
            # Create denomination logs
            for denom, count in denominations.items():
                if int(count) > 0:
                    DenominationLog.objects.create(
                        transaction=transaction,
                        denomination=int(denom),
                        quantity_inserted=int(count),
                        quantity_returned=0
                    )
            
            # Calculate change denominations
            change_denominations = calculate_change_denominations(change)
            print(f"Change denominations: {change_denominations}")
            
            # Create change denomination logs
            for denom, count in change_denominations.items():
                if count > 0:
                    DenominationLog.objects.create(
                        transaction=transaction,
                        denomination=denom,
                        quantity_inserted=0,
                        quantity_returned=count
                    )
            
            # Set purchased products
            purchased_products = [{
                'product_id': product.product_id,
                'name': product.name,
                'quantity': quantity,
                'price': float(product.price)
            }]
            transaction.set_products_purchased(purchased_products)
            transaction.save()
            
            print("=== PURCHASE SUCCESSFUL ===")
            
            return JsonResponse({
                'status': 'success',
                'message': f'Enjoy your {product.name}!',
                'change': change,
                'change_denominations': change_denominations
            })
            
        except Exception as e:
            print(f"=== ERROR IN PROCESS_PURCHASE ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            print("=== END ERROR ===")
            
            return JsonResponse({
                'status': 'error', 
                'message': f'Server error: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def calculate_change_denominations(change_amount):
    """
    Calculate how to give change using available denominations
    Returns a dictionary of denomination: count
    """
    denominations = [500, 200, 100, 50, 20, 10, 5]
    change_denominations = {}
    
    # Convert to integer (rupees)
    remaining = int(round(change_amount))
    
    for denom in denominations:
        count = remaining // denom
        if count > 0:
            change_denominations[denom] = count
            remaining %= denom
    
    return change_denominations

def transaction_history(request):
    """
    Big Data: Display all transactions with detailed denomination logs
    """
    transactions = Transaction.objects.all().order_by('-timestamp')
    
    # Prepare detailed transaction data
    transaction_data = []
    for transaction in transactions:
        # Get denomination details
        denomination_logs = DenominationLog.objects.filter(transaction=transaction)
        
        # Calculate inserted and returned details
        inserted_details = []
        returned_details = []
        
        for log in denomination_logs:
            if log.quantity_inserted > 0:
                inserted_details.append(f"Rs {log.denomination} × {log.quantity_inserted}")
            if log.quantity_returned > 0:
                returned_details.append(f"Rs {log.denomination} × {log.quantity_returned}")
        
        # Get purchased products
        purchased_products = transaction.get_products_purchased()
        
        transaction_data.append({
            'transaction': transaction,
            'inserted_details': ", ".join(inserted_details) if inserted_details else "None",
            'returned_details': ", ".join(returned_details) if returned_details else "None",
            'purchased_products': purchased_products
        })
    
    context = {
        'transaction_data': transaction_data
    }
    return render(request, 'vending/history.html', context)